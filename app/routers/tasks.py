from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.redis_storage import redis_storage
from app.queue_manager import task_queue
from app.tasks import sync_cpu_bound
from app.logger import log_info, log_success, log_error
import asyncio

router = APIRouter()

notify_router = APIRouter(prefix="/notify", tags=["notifications"])

def send_email(email: str, message: str):
    import time
    time.sleep(2)
    print(f"✅ Email sent to {email}: {message}")

@notify_router.post("/email")
async def notify_email(email: str, message: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, message)
    log_info(f"Email уведомление запланировано для {email}")
    return {"status": "email will be sent in background"}

tasks_router = APIRouter(prefix="/tasks", tags=["long tasks"])

@tasks_router.post("/process")
async def start_processing(input_data: dict):
    """Запуск задачи с хранением в Redis"""
    task_id = await redis_storage.create_task()

    await task_queue.add_task(task_id, input_data)
    
    return {
        "task_id": task_id,
        "status": "queued",
        "queue_position": await task_queue.get_queue_size(),
        "storage": "redis"
    }

@tasks_router.get("/{task_id}")
async def get_task_status(task_id: str):
    """Получение статуса задачи из Redis"""
    task = await redis_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@tasks_router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Удаление задачи из Redis"""
    task = await redis_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await redis_storage.delete_task(task_id)
    log_info(f"Задача {task_id} удалена")
    return {"message": f"Task {task_id} deleted"}

@tasks_router.post("/compute")
async def compute_sync(data: dict):
    """CPU-bound задача в отдельном потоке"""
    log_info(f"Запуск CPU-bound вычисления с данными: {data}")
    result = await asyncio.to_thread(sync_cpu_bound, data)
    log_success(f"CPU-bound вычисление завершено: {result}")
    return result

@tasks_router.get("/stats/all")
async def get_redis_stats():
    """Статистика из Redis"""
    stats = await redis_storage.get_stats()
    stats["queue_size"] = await task_queue.get_queue_size()
    return stats

@tasks_router.get("/active/all")
async def get_active_tasks():
    """Список активных задач"""
    tasks = await redis_storage.get_active_tasks()
    return {"active_tasks": tasks, "count": len(tasks)}

router.include_router(notify_router)
router.include_router(tasks_router)