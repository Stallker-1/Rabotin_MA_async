import asyncio
import time
from app.storage import update_task

async def long_running_task(task_id: str, input_data: dict):
    """Длительная задача с прогрессом"""
    try:
        total_steps = 10
        for step in range(1, total_steps + 1):
            await asyncio.sleep(1)  # имитация работы
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
        print(f"✅ Задача {task_id} завершена")
        
        # Отправляем callback, если указан URL
        if "callback_url" in input_data:
            await send_simple_callback(input_data["callback_url"], task_id, result)
            
    except Exception as e:
        update_task(task_id, "error", result={"error": str(e)})
        print(f"❌ Ошибка задачи {task_id}: {e}")

def sync_cpu_bound(data: dict) -> dict:
    """Синхронная CPU-bound задача (блокирующая)"""
    print(f"🖥️ Выполняется CPU-bound задача с data={data}")
    time.sleep(3)  # блокирующий вызов
    result = {"computed": data.get("value", 0) * 2}
    print(f"✅ CPU-bound задача завершена: {result}")
    return result

async def send_simple_callback(callback_url: str, task_id: str, result: dict):
    """Простая отправка callback"""
    try:
        import httpx
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
                print(f"📞 Callback отправлен на {callback_url}")
            else:
                print(f"⚠️ Callback вернул код {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка отправки callback: {e}")