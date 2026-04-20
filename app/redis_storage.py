import json
from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime
import redis.asyncio as redis
from app.config import settings
from app.logger import log_info, log_error, log_success

class RedisTaskStorage:
    def __init__(self):
        self.redis = None
        self.ttl = settings.redis_task_ttl
    
    async def connect(self):
        """Подключение к Redis"""
        try:
            self.redis = await redis.from_url(
                settings.redis_url, 
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Проверяем подключение
            await self.redis.ping()
            log_success(f"Подключено к Redis: {settings.redis_url}")
        except Exception as e:
            log_error(f"Ошибка подключения к Redis: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            await self.redis.close()
            log_info("Отключено от Redis")
    
    async def create_task(self) -> str:
        """Создание новой задачи"""
        task_id = str(uuid4())
        task_data = {
            "task_id": task_id,
            "status": "pending",
            "result": None,
            "created_at": datetime.now().isoformat(),
            "progress": 0
        }
        
        # Сохраняем задачу с TTL (автоматическое удаление)
        await self.redis.setex(
            f"task:{task_id}",
            self.ttl,
            json.dumps(task_data, ensure_ascii=False)
        )
        
        # Добавляем ID задачи в список активных задач
        await self.redis.sadd("active_tasks", task_id)
        
        log_info(f"Задача создана в Redis: {task_id}")
        return task_id
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Получение задачи по ID"""
        data = await self.redis.get(f"task:{task_id}")
        if data:
            return json.loads(data)
        return None
    
    async def update_task(
        self, 
        task_id: str, 
        status: str, 
        result: Any = None, 
        progress: int = None
    ):
        """Обновление статуса задачи"""
        task_data = await self.get_task(task_id)
        if task_data:
            task_data["status"] = status
            task_data["updated_at"] = datetime.now().isoformat()
            
            if result is not None:
                task_data["result"] = result
            if progress is not None:
                task_data["progress"] = progress
            
            # Обновляем задачу с тем же TTL
            await self.redis.setex(
                f"task:{task_id}",
                self.ttl,
                json.dumps(task_data, ensure_ascii=False)
            )
            
            # Если задача завершена или с ошибкой, удаляем из активных
            if status in ["completed", "error"]:
                await self.redis.srem("active_tasks", task_id)
            
            log_info(f"Задача обновлена: {task_id} - {status} ({progress}%)")
    
    async def delete_task(self, task_id: str):
        """Удаление задачи"""
        await self.redis.delete(f"task:{task_id}")
        await self.redis.srem("active_tasks", task_id)
        log_info(f"Задача удалена: {task_id}")
    
    async def get_active_tasks(self) -> list:
        """Получение списка активных задач"""
        active_ids = await self.redis.smembers("active_tasks")
        tasks = []
        
        for task_id in active_ids:
            task = await self.get_task(task_id)
            if task:
                tasks.append(task)
        
        return tasks
    
    async def get_stats(self) -> dict:
        """Получение статистики по задачам"""
        active_ids = await self.redis.smembers("active_tasks")
        stats = {
            "total_active": len(active_ids),
            "tasks_by_status": {}
        }
        
        for task_id in active_ids:
            task = await self.get_task(task_id)
            if task:
                status = task.get("status", "unknown")
                stats["tasks_by_status"][status] = stats["tasks_by_status"].get(status, 0) + 1
        
        return stats
    
    async def cleanup_expired(self):
        """Очистка просроченных задач (Redis делает это автоматически по TTL)"""
        pass

# Глобальный экземпляр
redis_storage = RedisTaskStorage()