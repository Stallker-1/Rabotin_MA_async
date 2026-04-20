from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime, timedelta
import asyncio

# Хранилище задач
tasks_storage: Dict[str, Dict[str, Any]] = {}

# Очередь задач
task_queue = asyncio.Queue()
is_worker_running = False

# Время жизни задачи (минуты)
TASK_LIFETIME_MINUTES = 10

def create_task() -> str:
    task_id = str(uuid4())
    tasks_storage[task_id] = {
        "status": "pending",
        "result": None,
        "created_at": datetime.now().isoformat(),
        "progress": 0
    }
    print(f"📋 Задача {task_id} создана")
    return task_id

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    return tasks_storage.get(task_id)

def update_task(task_id: str, status: str, result: Any = None, progress: int = None):
    if task_id in tasks_storage:
        tasks_storage[task_id]["status"] = status
        if result is not None:
            tasks_storage[task_id]["result"] = result
        if progress is not None:
            tasks_storage[task_id]["progress"] = progress
        tasks_storage[task_id]["updated_at"] = datetime.now().isoformat()
        print(f"📊 Задача {task_id}: {status} (прогресс: {progress}%)")

def cleanup_old_tasks():
    """Удаляет задачи старше TASK_LIFETIME_MINUTES"""
    now = datetime.now()
    to_delete = []
    
    for task_id, task in tasks_storage.items():
        created_at = datetime.fromisoformat(task["created_at"])
        if now - created_at > timedelta(minutes=TASK_LIFETIME_MINUTES):
            to_delete.append(task_id)
    
    for task_id in to_delete:
        del tasks_storage[task_id]
        print(f"🗑️ Удалена старая задача {task_id}")
    
    if to_delete:
        print(f"Очищено {len(to_delete)} старых задач")

async def auto_cleanup():
    """Фоновая задача для периодической очистки"""
    while True:
        await asyncio.sleep(60)  # Проверяем каждую минуту
        cleanup_old_tasks()
        print(f"📊 В хранилище {len(tasks_storage)} активных задач")

async def worker():
    """Воркер для обработки задач из очереди"""
    global is_worker_running
    is_worker_running = True
    
    # Импортируем здесь, чтобы избежать циклического импорта
    from app.tasks import long_running_task
    
    while is_worker_running:
        try:
            task_id, input_data = await task_queue.get()
            print(f"🔄 Воркер начал обработку задачи {task_id}")
            await long_running_task(task_id, input_data)
            print(f"✅ Воркер закончил задачу {task_id}")
            task_queue.task_done()
        except Exception as e:
            print(f"❌ Ошибка воркера: {e}")
            await asyncio.sleep(1)