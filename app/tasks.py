import asyncio
import httpx
from app.storage import update_task
from app.logger import log_info, log_error, log_success

async def send_simple_callback(callback_url: str, task_id: str, result: dict):
    """Простая отправка callback без повторных попыток"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                callback_url,
                json={
                    "task_id": task_id,
                    "result": result,
                    "status": "completed"
                },
                timeout=5.0
            )
            if response.status_code == 200:
                log_success(f"Callback отправлен на {callback_url}")
                print(f"📞 Callback отправлен на {callback_url}")
            else:
                log_info(f"Callback вернул код {response.status_code}")
                print(f"⚠️ Callback вернул код {response.status_code}")
    except Exception as e:
        log_error(f"Ошибка отправки callback: {e}")
        print(f"❌ Ошибка отправки callback: {e}")

async def long_running_task(task_id: str, input_data: dict):
    try:
        total_steps = 10
        for step in range(1, total_steps + 1):
            await asyncio.sleep(1)
            progress = int((step / total_steps) * 100)
            update_task(task_id, "running", progress=progress)
            print(f"📊 Задача {task_id}: прогресс {progress}%")
        
        # Финальный результат
        result = {
            "output": f"Processed {input_data.get('name', 'unknown')}",
            "steps": total_steps,
            "input": input_data
        }
        update_task(task_id, "completed", result=result, progress=100)
        log_success(f"Задача {task_id} завершена")
        print(f"✅ Задача {task_id} завершена")
        
        # Отправляем callback, если указан URL
        if "callback_url" in input_data:
            await send_simple_callback(input_data["callback_url"], task_id, result)
            
    except Exception as e:
        update_task(task_id, "error", result={"error": str(e)})
        log_error(f"Ошибка задачи {task_id}: {e}")
        print(f"❌ Ошибка задачи {task_id}: {e}")

def sync_cpu_bound(data: dict) -> dict:
    """Имитация тяжелых вычислений (блокирующий код)"""
    import time
    time.sleep(3)  # блокирующий вызов
    return {"computed": data.get("value", 0) * 2}