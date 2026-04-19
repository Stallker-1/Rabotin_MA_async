from typing import Any, Dict
from uuid import uuid4

tasks_storage: dict[str, Dict[str, Any]] = {}


def create_task() -> str:
    task_id = str(uuid4())
    tasks_storage[task_id] = {
        "status": "pending",
        "result": None,
    }
    return task_id


def update_task(task_id: str, status: str, result: Any = None):
    if task_id in tasks_storage:
        tasks_storage[task_id]["status"] = status
        if result is not None:
            tasks_storage[task_id]["result"] = result


def get_task(task_id: str):
    return tasks_storage.get(task_id)