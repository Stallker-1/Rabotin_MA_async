from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.routers import tasks_router, websocket_router
from app.redis_storage import redis_storage
from app.queue_manager import task_queue
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Подключаемся к Redis
    await redis_storage.connect()
    
    # Запускаем очередь задач
    await task_queue.start()
    
    print(f"🚀 Приложение {settings.app_name} запущено")
    print(f"📊 Redis: {settings.redis_url}")
    
    yield
    
    await task_queue.stop()
    
    await redis_storage.disconnect()
    
    print("🛑 Приложение остановлено")

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(tasks_router)
app.include_router(websocket_router)

@app.get("/")
async def root():
    return {
        "message": "Hello, Async FastAPI with Redis!",
        "redis": settings.redis_url
    }

@app.get("/health")
async def health():
    """Проверка здоровья приложения"""
    try:
        await redis_storage.redis.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "queue_size": await task_queue.get_queue_size()
    }