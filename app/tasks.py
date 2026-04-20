import asyncio
import httpx
import json
from app.redis_storage import redis_storage
from app.logger import log_info, log_error, log_success

async def send_simple_callback(callback_url: str, task_id: str, result: dict):
    """Отправка callback уведомления"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                callback_url,
                json={
                    "task_id": task_id,
                    "result": result,
                    "status": "completed",
                    "timestamp": asyncio.get_event_loop().time()
                },
                timeout=5.0
            )
            if response.status_code == 200:
                log_success(f"Callback отправлен на {callback_url}")
            else:
                log_error(f"Callback ошибка: код {response.status_code}")
    except Exception as e:
        log_error(f"Callback не удался: {e}")

async def long_running_task_redis(task_id: str, input_data: dict):
    """Длительная задача с хранением в Redis"""
    try:
        total_steps = 10
        
        for step in range(1, total_steps + 1):
            await asyncio.sleep(1)  # Имитация работы
            progress = int((step / total_steps) * 100)
            
            # Обновляем прогресс в Redis
            await redis_storage.update_task(
                task_id, 
                "running", 
                progress=progress
            )
            
            log_info(f"Задача {task_id}: прогресс {progress}%")
        
        # Финальный результат
        result = {
            "output": f"Processed {input_data.get('name', 'unknown')}",
            "steps": total_steps,
            "input": input_data,
            "completed_at": asyncio.get_event_loop().time()
        }
        
        # Обновляем статус в Redis
        await redis_storage.update_task(
            task_id, 
            "completed", 
            result=result, 
            progress=100
        )
        
        log_success(f"Задача {task_id} успешно завершена")
        
        # Отправляем callback если указан
        if input_data.get("callback_url"):
            await send_simple_callback(
                input_data["callback_url"], 
                task_id, 
                result
            )
            
    except Exception as e:
        error_msg = str(e)
        await redis_storage.update_task(
            task_id, 
            "error", 
            result={"error": error_msg}
        )
        log_error(f"Задача {task_id} завершилась ошибкой: {error_msg}")

# Старая версия для совместимости (без Redis)
async def long_running_task(task_id: str, input_data: dict):
    """Длительная задача с in-memory хранилищем (для обратной совместимости)"""
    from app.storage import update_task
    
    try:
        total_steps = 10
        for step in range(1, total_steps + 1):
            await asyncio.sleep(1)
            progress = int((step / total_steps) * 100)
            update_task(task_id, "running", progress=progress)
        
        result = {
            "output": f"Processed {input_data.get('name', 'unknown')}",
            "steps": total_steps,
            "input": input_data
        }
        update_task(task_id, "completed", result=result, progress=100)
        
        if input_data.get("callback_url"):
            await send_simple_callback(input_data["callback_url"], task_id, result)
            
    except Exception as e:
        update_task(task_id, "error", result={"error": str(e)})

def sync_cpu_bound(data: dict) -> dict:
    """Синхронная CPU-bound задача"""
    import time
    time.sleep(3)
    return {"computed": data.get("value", 0) * 2}