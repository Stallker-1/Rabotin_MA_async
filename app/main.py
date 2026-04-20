from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config import settings
from app.routers import tasks_router, websocket_router
from app.storage import worker, is_worker_running

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем воркер при старте приложения
    import asyncio
    asyncio.create_task(worker())
    print("🚀 Воркер очереди задач запущен")
    yield
    # Останавливаем воркер при выключении
    global is_worker_running
    is_worker_running = False
    print("🛑 Воркер очереди задач остановлен")

app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.include_router(tasks_router)
app.include_router(websocket_router)

@app.get("/")
async def root():
    return {"message": "Hello, Async FastAPI!"}