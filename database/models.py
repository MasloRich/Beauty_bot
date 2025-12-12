import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self, config):
        """Подключаемся к PostgreSQL"""
        logger.info(f"🔗 Подключаемся к PostgreSQL: {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
        
        try:
            self.pool = await asyncpg.create_pool(
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.BOT_TOKEN,
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
        
        # Таблица мастеров
        await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS masters (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                full_name VARCHAR(200) NOT NULL,
                experience TEXT,
                percentage INTEGER DEFAULT 40 CHECK (percentage BETWEEN 0 AND 100),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица клиентов
        await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100),
                phone VARCHAR(20),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица услуг
        await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                master_id INTEGER REFERENCES masters(id) ON DELETE CASCADE,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
                price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица расписания мастеров
        await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS master_schedule (
                id SERIAL PRIMARY KEY,
                master_id INTEGER REFERENCES masters(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(master_id, date, start_time)
            )
        ''')
        
        # Таблица записей
        await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                client_id INTEGER REFERENCES clients(id) ON DELETE SET NULL,
                master_id INTEGER REFERENCES masters(id) ON DELETE CASCADE,
                service_id INTEGER REFERENCES services(id),
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')),
                source VARCHAR(50) DEFAULT 'bot' CHECK (source IN ('bot', 'master')),
                paid_amount DECIMAL(10,2) DEFAULT 0,
                procedure_notes TEXT,
                notification_sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (end_time > start_time)
            )
        ''')
        
        # Индексы для быстрого поиска
        await self.pool.execute('CREATE INDEX IF NOT EXISTS idx_appointments_master_date ON appointments(master_id, start_time)')
        await self.pool.execute('CREATE INDEX IF NOT EXISTS idx_appointments_client ON appointments(client_id)')
        await self.pool.execute('CREATE INDEX IF NOT EXISTS idx_schedule_master_date ON master_schedule(master_id, date)')
        
        logger.info("✅ Все таблицы успешно созданы (или уже существовали)")
        
        # Проверяем существование таблиц
        conn = await self.pool.acquire()
        try:
            tables = await conn.fetch('''
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            ''')
            
            logger.info(f"📊 Создано таблиц: {len(tables)}")
            for table in tables:
                logger.info(f"   • {table['table_name']}")
        finally:
            await self.pool.release(conn)