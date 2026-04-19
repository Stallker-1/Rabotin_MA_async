import asyncio
import time
from app.storage import update_task

async def long_running_task(task_id: str, input_data: dict):
    try:
        total_steps = 10

        for step in range(1, total_steps + 1):
            await asyncio.sleep(1)

            update_task(
                task_id,
                "running",
                {
                    "progress": step,
                    "total": total_steps,
                },
            )

        result = {
            "output": f"Processed {input_data.get('name', 'unknown')}",
            "success": True,
        }

        update_task(task_id, "completed", result)

    except Exception as e:
        update_task(task_id, "error", {"error": str(e)})

def sync_cpu_bound(data: dict) -> dict:
    # Имитация вычислений, занимающих несколько секунд
    time.sleep(3)  # блокирует поток
    return {"computed": data.get("value", 0) * 2}