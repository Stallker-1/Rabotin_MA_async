from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.storage import create_task, get_task, task_queue, cleanup_old_tasks, tasks_storage
from app.tasks import long_running_task, sync_cpu_bound
from app.logger import log_info, log_task, log_success
import asyncio

router = APIRouter()

# Роутер для уведомлений
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

# Роутер для длительных задач
tasks_router = APIRouter(prefix="/tasks", tags=["long tasks"])

@tasks_router.post("/process")
async def start_processing(input_data: dict):
    """Задача попадает в очередь, а не выполняется сразу"""
    task_id = create_task()
    # Добавляем задачу в очередь
    await task_queue.put((task_id, input_data))
    log_task(task_id, "ДОБАВЛЕНА В ОЧЕРЕДЬ", f"позиция: {task_queue.qsize()}")
    print(f"📋 Задача {task_id} добавлена в очередь (в очереди: {task_queue.qsize()})")
    return {
        "task_id": task_id,
        "status": "queued",
        "queue_position": task_queue.qsize()
    }

@tasks_router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@tasks_router.post("/compute")
async def compute_sync(data: dict):
    """CPU-bound задача в отдельном потоке"""
    log_info(f"Запуск CPU-bound вычисления с данными: {data}")
    result = await asyncio.to_thread(sync_cpu_bound, data)
    log_success(f"CPU-bound вычисление завершено: {result}")
    return result

@tasks_router.delete("/cleanup")
async def manual_cleanup():
    """Ручная очистка старых задач"""
    before_count = len(tasks_storage)
    cleanup_old_tasks()
    after_count = len(tasks_storage)
    log_info(f"Ручная очистка: удалено {before_count - after_count} задач")
    return {
        "message": f"Очищено {before_count - after_count} старых задач",
        "remaining_tasks": after_count
    }

@tasks_router.get("/stats")
async def get_stats():
    """Статистика по задачам"""
    stats = {
        "total_tasks": len(tasks_storage),
        "queue_size": task_queue.qsize(),
        "tasks_by_status": {}
    }
    
    for task in tasks_storage.values():
        status = task["status"]
        stats["tasks_by_status"][status] = stats["tasks_by_status"].get(status, 0) + 1
    
    return stats

# Подключаем роутеры
router.include_router(notify_router)
router.include_router(tasks_router)