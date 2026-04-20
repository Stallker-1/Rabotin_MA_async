import asyncio
from typing import Dict, Any
from app.redis_storage import redis_storage
from app.logger import log_info, log_error

class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.worker_task = None
        self.is_running = False
    
    async def add_task(self, task_id: str, input_data: dict):
        """Добавление задачи в очередь"""
        await self.queue.put((task_id, input_data))
        # Сохраняем входные данные задачи в Redis
        await redis_storage.redis.setex(
            f"task_input:{task_id}",
            3600,
            json.dumps(input_data)
        )
        log_info(f"Задача {task_id} добавлена в очередь (позиция: {self.queue.qsize()})")
    
    async def worker(self):
        """Воркер, обрабатывающий задачи последовательно"""
        from app.tasks import long_running_task_redis
        
        while self.is_running:
            try:
                task_id, input_data = await self.queue.get()
                log_info(f"Воркер начал обработку задачи {task_id}")

                await long_running_task_redis(task_id, input_data)
                
                log_success(f"Воркер завершил задачу {task_id}")
                self.queue.task_done()

                await redis_storage.redis.delete(f"task_input:{task_id}")
                
            except Exception as e:
                log_error(f"Ошибка воркера: {e}")
                await asyncio.sleep(1)
    
    async def start(self):
        """Запуск воркера"""
        self.is_running = True
        self.worker_task = asyncio.create_task(self.worker())
        log_info("Воркер очереди задач запущен")
    
    async def stop(self):
        """Остановка воркера"""
        self.is_running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        log_info("Воркер очереди задач остановлен")
    
    async def get_queue_size(self) -> int:
        """Получение размера очереди"""
        return self.queue.qsize()

task_queue = TaskQueue()