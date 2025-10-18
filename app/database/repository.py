import asyncpg
import logging
from typing import List, Optional
from .models import User, Admin, Order, Transaction

logger = logging.getLogger(__name__)

class DatabaseRepository:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        """ایجاد connection pool"""
        try:
            self.pool = await asyncpg.create_pool(self.database_url)
            await self.init_db()
            logger.info("✅ Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def init_db(self):
        """ایجاد جداول دیتابیس"""
        commands = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255),
                balance INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS admins (
                admin_id BIGINT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                first_name VARCHAR(255) NOT NULL,
                level VARCHAR(20) DEFAULT 'admin',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by BIGINT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                plan_type VARCHAR(50) NOT NULL,
                amount INTEGER NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                receipt_file_id VARCHAR(500),
                vpn_config TEXT,
                vpn_config_text TEXT,
                config_type VARCHAR(10) DEFAULT 'file',
                admin_notes TEXT,
                processed_by BIGINT REFERENCES admins(admin_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                amount INTEGER NOT NULL,
                type VARCHAR(20) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS logs (
                log_id SERIAL PRIMARY KEY,
                user_id BIGINT,
                action VARCHAR(255) NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        async with self.pool.acquire() as conn:
            for command in commands:
                await conn.execute(command)
        logger.info("✅ Database tables created successfully")
    
    async def add_user(self, user: User) -> bool:
        """افزودن کاربر جدید"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    updated_at = CURRENT_TIMESTAMP
                """, user.user_id, user.username, user.first_name, user.last_name)
            return True
        except Exception as e:
            logger.error(f"خطا در افزودن کاربر: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """دریافت اطلاعات کاربر"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
                return User(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"خطا در دریافت کاربر: {e}")
            return None
    
    async def create_order(self, order: Order) -> Optional[int]:
        """ایجاد سفارش جدید"""
        try:
            async with self.pool.acquire() as conn:
                order_id = await conn.fetchval("""
                    INSERT INTO orders (user_id, plan_type, amount)
                    VALUES ($1, $2, $3)
                    RETURNING order_id
                """, order.user_id, order.plan_type, order.amount)
                return order_id
        except Exception as e:
            logger.error(f"خطا در ایجاد سفارش: {e}")
            return None
    
    async def update_order_receipt(self, order_id: int, receipt_file_id: str) -> bool:
        """بروزرسانی رسید پرداخت"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE orders 
                    SET receipt_file_id = $1, status = 'waiting', updated_at = CURRENT_TIMESTAMP
                    WHERE order_id = $2
                """, receipt_file_id, order_id)
                return True
        except Exception as e:
            logger.error(f"خطا در بروزرسانی سفارش: {e}")
            return False
    
    async def update_order_config(self, order_id: int, config_text: str, config_type: str, processed_by: int) -> bool:
        """بروزرسانی کانفیگ سفارش"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE orders 
                    SET vpn_config_text = $1, config_type = $2, 
                        processed_by = $3, status = 'completed',
                        updated_at = CURRENT_TIMESTAMP
                    WHERE order_id = $4
                """, config_text, config_type, processed_by, order_id)
                return True
        except Exception as e:
            logger.error(f"خطا در بروزرسانی کانفیگ سفارش: {e}")
            return False
    
    async def get_order(self, order_id: int) -> Optional[Order]:
        """دریافت اطلاعات سفارش"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM orders WHERE order_id = $1", order_id)
                return Order(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"خطا در دریافت سفارش: {e}")
            return None
    
    async def get_user_orders(self, user_id: int, limit: int = 10) -> List[Order]:
        """دریافت سفارشات کاربر"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM orders 
                    WHERE user_id = $1 
                    ORDER BY created_at DESC 
                    LIMIT $2
                """, user_id, limit)
                return [Order(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"خطا در دریافت سفارشات کاربر: {e}")
            return []
    
    async def get_pending_orders(self) -> List[Order]:
        """دریافت سفارشات در انتظار"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT o.*, u.username, u.first_name 
                    FROM orders o 
                    JOIN users u ON o.user_id = u.user_id 
                    WHERE o.status = 'waiting'
                    ORDER BY o.created_at DESC
                """)
                return [Order(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"خطا در دریافت سفارشات pending: {e}")
            return []
    
    async def get_all_users(self) -> List[User]:
        """دریافت تمام کاربران"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
                return [User(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"خطا در دریافت کاربران: {e}")
            return []
    
    async def add_admin(self, admin: Admin) -> bool:
        """افزودن ادمین جدید"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO admins (admin_id, username, first_name, level, created_by)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (admin_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    level = EXCLUDED.level,
                    is_active = TRUE
                """, admin.admin_id, admin.username, admin.first_name, admin.level, admin.created_by)
                return True
        except Exception as e:
            logger.error(f"خطا در افزودن ادمین: {e}")
            return False
    
    async def get_admin(self, admin_id: int) -> Optional[Admin]:
        """دریافت اطلاعات ادمین"""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM admins WHERE admin_id = $1", admin_id)
                return Admin(**dict(row)) if row else None
        except Exception as e:
            logger.error(f"خطا در دریافت ادمین: {e}")
            return None
    
    async def get_all_admins(self) -> List[Admin]:
        """دریافت تمام ادمین‌ها"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM admins ORDER BY created_at DESC")
                return [Admin(**dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"خطا در دریافت ادمین‌ها: {e}")
            return []
    
    async def log_admin_action(self, admin_id: int, action: str, target_id: int, details: str):
        """ثبت لاگ فعالیت ادمین"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO logs (user_id, action, details)
                    VALUES ($1, $2, $3)
                """, admin_id, action, details)
        except Exception as e:
            logger.error(f"خطا در ثبت لاگ: {e}")
