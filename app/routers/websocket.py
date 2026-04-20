from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.redis_storage import redis_storage
from app.logger import log_info, log_error
import asyncio
import json

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/task/{task_id}")
async def websocket_task_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    log_info(f"WebSocket подключен для задачи {task_id}")
    
    try:
        last_progress = -1
        
        while True:
            task = await redis_storage.get_task(task_id)
            
            if not task:
                await websocket.send_json({"error": "Task not found"})
                log_error(f"WebSocket: задача {task_id} не найдена")
                break
            
            current_progress = task.get("progress", 0)
            if current_progress != last_progress or task.get("status") in ["completed", "error"]:
                await websocket.send_json({
                    "task_id": task_id,
                    "status": task.get("status"),
                    "progress": current_progress,
                    "result": task.get("result"),
                    "timestamp": asyncio.get_event_loop().time()
                })
                last_progress = current_progress
            
            if task.get("status") in ["completed", "error"]:
                log_info(f"WebSocket отключен для задачи {task_id} (завершена)")
                break
            
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        log_info(f"WebSocket отключен для задачи {task_id} (клиент закрыл соединение)")
    except Exception as e:
        log_error(f"WebSocket ошибка для задачи {task_id}: {e}")