import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def add_test_data(self, conn):
        """Добавить тестовые данные для разработки"""
        
        # Проверяем есть ли уже тестовые данные
        masters_count = await conn.fetchval("SELECT COUNT(*) FROM masters")
        
        if masters_count == 0:
            logger.info("➕ Добавляем тестовые данные...")
            
            # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: Используем чистые строки ASCII для теста
            # Позже заменим на реальные русские названия когда база заработает
            
            # Временные английские названия для теста
            masters = [
                (123456789, 'Anna Ivanova', 'Experience 5 years', 40),
                (987654321, 'Maria Petrova', 'Experience 3 years', 40),
                (555555555, 'Elena Sidorova', 'Experience 7 years', 40),
            ]
            
            for telegram_id, full_name, experience, percentage in masters:
                await conn.execute(
                    """
                    INSERT INTO masters (telegram_id, full_name, experience, percentage)
                    VALUES ($1, $2, $3, $4)
                    """,
                    telegram_id, full_name, experience, percentage
                )
            
            # Получаем ID мастеров
            master_records = await conn.fetch("SELECT id FROM masters ORDER BY id")
            
            # Временные английские названия услуг
            services = [
                (master_records[0]['id'], 'Eyelash extensions', 'Full set extensions', 120, 2500),
                (master_records[0]['id'], 'Eyelash lifting', 'Lifting with tinting', 90, 2000),
                (master_records[1]['id'], 'Eyebrow correction', 'Correction with coloring', 60, 1500),
                (master_records[1]['id'], 'Eyebrow shaping', 'Wax shaping', 45, 1200),
                (master_records[2]['id'], 'Eyelash SPA', 'Complex care procedure', 120, 3000),
            ]
            
            for master_id, name, description, duration, price in services:
                await conn.execute(
                    """
                    INSERT INTO services (master_id, name, description, duration_minutes, price)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    master_id, name, description, duration, price
                )
            
            # Добавляем расписание на ближайшие 7 дней
            from datetime import datetime, timedelta, time
            
            for i in range(7):
                current_date = datetime.now().date() + timedelta(days=i+1)
                
                for master_record in master_records:
                    master_id = master_record['id']
                    # Добавляем рабочий день (10:00-18:00) в будни
                    if current_date.weekday() < 5:  # Пн-Пт
                        await conn.execute(
                            """
                            INSERT INTO master_schedule (master_id, date, start_time, end_time)
                            VALUES ($1, $2, $3, $4)
                            """,
                            master_id, current_date, time(10, 0), time(18, 0)
                        )
            
            logger.info("✅ Тестовые данные добавлены (английские названия)")
        else:
            logger.info("📊 В базе уже есть данные")
    
    async def connect(self, config):
        """Подключаемся к PostgreSQL"""
        logger.info(f"🔗 Подключаемся к PostgreSQL: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
        
        try:
            self.pool = await asyncpg.create_pool(
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                host=config.DB_HOST,
                port=config.DB_PORT,
                min_size=1,
                max_size=10
            )
            
            logger.info("✅ Подключение к PostgreSQL установлено")
            await self.create_tables()
            
        except asyncpg.InvalidPasswordError:
            logger.error("❌ Неверный пароль PostgreSQL. Проверьте .env файл")
            raise
        except asyncpg.ConnectionDoesNotExistError:
            logger.error("❌ PostgreSQL недоступен. Убедитесь что сервер запущен")
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к PostgreSQL: {e}")
            raise
    
    async def create_tables(self):
        """Создаем все необходимые таблицы"""
        
        # Используем контекстный менеджер для подключения
        async with self.pool.acquire() as conn:
            # Создаем таблицы...
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS masters (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    full_name VARCHAR(200) NOT NULL,
                    experience TEXT,
                    percentage INTEGER DEFAULT 40,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # ... остальные таблицы
            
            logger.info("✅ Все таблицы успешно созданы")
            
            # Проверяем таблицы
            tables = await conn.fetch('''
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            ''')
            
            logger.info(f"📊 Создано таблиц: {len(tables)}")
            
            # Добавляем тестовые данные
            await self.add_test_data(conn)