from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.storage import get_task
from app.logger import log_info, log_error
import asyncio
import json

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/task/{task_id}")
async def websocket_task_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    log_info(f"WebSocket подключен для задачи {task_id}")
    
    try:
        while True:
            task = get_task(task_id)
            if not task:
                await websocket.send_json({"error": "Task not found"})
                log_error(f"WebSocket: задача {task_id} не найдена")
                break
            
            # Отправляем текущий статус
            await websocket.send_json({
                "task_id": task_id,
                "status": task.get("status"),
                "progress": task.get("progress", 0),
                "result": task.get("result")
            })
            
            # Если задача завершена или с ошибкой - закрываем соединение
            if task.get("status") in ["completed", "error"]:
                log_info(f"WebSocket отключен для задачи {task_id} (задача завершена)")
                break
            
            await asyncio.sleep(1)  # Опрашиваем каждую секунду
            
    except WebSocketDisconnect:
        log_info(f"WebSocket отключен для задачи {task_id} (клиент закрыл соединение)")
    except Exception as e:
        log_error(f"WebSocket ошибка для задачи {task_id}: {e}")