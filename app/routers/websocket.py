from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.storage import get_task
import asyncio

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/task/{task_id}")
async def websocket_task_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        while True:
            task = get_task(task_id)
            if not task:
                await websocket.send_json({"error": "Task not found"})
                break
            await websocket.send_json(task)
            if task["status"] in ("completed", "error"):
                break
            await asyncio.sleep(1)  # интервал опроса хранилища     
    except WebSocketDisconnect:
        print(f"Client disconnected from task {task_id}")