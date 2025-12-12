import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Config:
    # Токен бота из .env файла
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # ID администраторов (преобразуем строку в список чисел)
    ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(','))) if os.getenv("ADMIN_IDS") else []
    
    # Настройки базы данных
    DB_NAME = os.getenv("DB_NAME", "beauty_bot")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Trigonometriya")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    # Redis для хранения состояний
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Для платежей (пока оставляем пустым)
    PAYMENT_TOKEN = os.getenv("PAYMENT_TOKEN", "")