from fastapi import FastAPI
from app.config import settings
from app.routers import tasks_router, websocket_router

app = FastAPI(title=settings.app_name)

app.include_router(tasks_router)
app.include_router(websocket_router)

@app.get("/")
async def root():
    return {"message": "Hello, Async FastAPI!"}