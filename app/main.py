from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.routers import tasks_router, websocket_router
from app.storage import worker, auto_cleanup, is_worker_running
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем воркер и автоочистку при старте приложения
    worker_task = asyncio.create_task(worker())
    cleanup_task = asyncio.create_task(auto_cleanup())
    print("🚀 Воркер очереди задач запущен")
    print("🧹 Автоочистка старых задач запущена")
    
    yield
    
    # Останавливаем воркер при выключении
    global is_worker_running
    is_worker_running = False
    worker_task.cancel()
    cleanup_task.cancel()
    print("🛑 Воркер очереди задач остановлен")

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(tasks_router)
app.include_router(websocket_router)

@app.get("/")
async def root():
    return {"message": "Hello, Async FastAPI!"}