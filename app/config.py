from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FastAPI Async Lab"
    redis_url: str = "redis://localhost:6379"
    redis_task_ttl: int = 3600
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()