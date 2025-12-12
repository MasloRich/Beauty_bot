import sys
import os

# Добавляем корневую папку проекта в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Теперь можно импортировать модули из корня

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from database.models import Database

# Импорты handlers
from bot.handlers import client_handlers, admin_handlers, master_handlers

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    """Главная функция запуска бота"""
    
    config = Config()
    
    if not config.BOT_TOKEN:
        logger.error("❌ Ошибка: BOT_TOKEN не найден в .env файле")
        return
    
    logger.info("🚀 Запускаем бота студии красоты...")
    
    try:
        # Инициализация базы данных
        logger.info("📀 Подключаемся к базе данных...")
        db = Database()
        await db.connect(config)
        
        # Настройка хранилища состояний
        logger.info("⚙️  Настраиваем хранилище...")
        
        # Пробуем Redis, если не работает - MemoryStorage
        storage = None
        try:
            storage = RedisStorage.from_url(config.REDIS_URL)
            logger.info("🔴 Используем Redis для хранения состояний")
        except Exception as e:
            logger.warning(f"⚠️  Redis недоступен, используем память: {e}")
            storage = MemoryStorage()
            logger.info("💾 Используем MemoryStorage (данные будут храниться в памяти)")
        
        # Создаем бота с настройками по умолчанию (правильный способ для aiogram 3.23.0)
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        dp = Dispatcher(storage=storage)
        
        # Подключаем роутеры (обработчики)
        dp.include_router(client_handlers.router)
        dp.include_router(admin_handlers.router)
        dp.include_router(master_handlers.router)
        
        logger.info("✅ Бот успешно инициализирован!")
        logger.info("📊 Проверяем подключения...")
        
        # Проверяем что бот доступен
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот: @{bot_info.username} ({bot_info.full_name})")
        
        # Удаляем вебхук если был (для чистого запуска)
        await bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("🎯 Бот готов к работе! Ожидаем сообщения...")
        logger.info("👉 Команды для тестирования:")
        logger.info("   • /start - для клиентов")
        logger.info("   • /master - для мастеров (нужен telegram_id в таблице masters)")
        logger.info("   • /admin - для администраторов (ID в ADMIN_IDS)")
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}", exc_info=True)
        logger.info("🔄 Перезапустите бота после исправления ошибки")

if __name__ == "__main__":
    asyncio.run(main())