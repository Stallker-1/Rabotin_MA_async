import logging
from datetime import datetime

# Настройка простого логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)

# Простые функции для логирования
def log_info(message: str):
    logger.info(f"ℹ️ {message}")

def log_success(message: str):
    logger.info(f"✅ {message}")

def log_error(message: str):
    logger.error(f"❌ {message}")

def log_warning(message: str):
    logger.warning(f"⚠️ {message}")

def log_task(task_id: str, action: str, details: str = ""):
    logger.info(f"📋 Задача {task_id} | {action} | {details}")