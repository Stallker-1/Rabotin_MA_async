from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime
import asyncio

tasks_storage: Dict[str, Dict[str, Any]] = {}
# Простая очередь задач
task_queue = asyncio.Queue()
is_worker_running = False

def create_task() -> str:
    task_id = str(uuid4())
    tasks_storage[task_id] = {
        "status": "pending",
        "result": None,
        "created_at": datetime.now().isoformat(),
        "progress": 0
    }
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

async def worker():
    """Простой воркер, обрабатывающий задачи из очереди"""
    global is_worker_running
    is_worker_running = True
    
    while is_worker_running:
        try:
            # Ждем задачу из очереди
            task_id, input_data = await task_queue.get()
            print(f"🔄 Воркер начал обработку задачи {task_id}")
            
            # Выполняем задачу
            await long_running_task(task_id, input_data)
            
            print(f"✅ Воркер закончил задачу {task_id}")
            task_queue.task_done()
        except Exception as e:
            print(f"❌ Ошибка воркера: {e}")
            await asyncio.sleep(1)

# Импортируем функцию задачи (будет определена позже)
from app.tasks import long_running_task