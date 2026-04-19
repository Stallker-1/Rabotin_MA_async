from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.storage import create_task, get_task
from app.tasks import long_running_task, sync_cpu_bound
import asyncio

router = APIRouter(prefix="/tasks", tags=["long tasks"])

@router.post("/process")
async def start_processing(
    input_data: dict,
    background_tasks: BackgroundTasks,
):
    task_id = create_task()

    background_tasks.add_task(
        long_running_task,
        task_id,
        input_data,
    )

    return {"task_id": task_id}

@router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = get_task(task_id)

    if not task:
        raise HTTPException(404, "Task not found")

    return task

@router.post("/compute")
async def compute_sync(data: dict):
    # Запускаем синхронную функцию в отдельном потоке, не блокируя event 
    result = await asyncio.to_thread(sync_cpu_bound, data)
    return result