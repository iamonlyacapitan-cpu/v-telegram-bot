import asyncpg
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """اتصال به دیتابیس"""
        try:
            self.pool = await asyncpg.create_pool(os.getenv('DATABASE_URL'))
            await self.create_tables()
            logger.info("✅ Connected to database successfully")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    async def create_tables(self):
        """ایجاد جداول مورد نیاز"""
        async with self.pool.acquire() as conn:
            # جدول کاربران
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    is_admin BOOLEAN DEFAULT FALSE,
                    balance INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # جدول پلن‌ها
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS plans (
                    plan_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    duration_days INTEGER NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # جدول سفارشات
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    plan_id INTEGER REFERENCES plans(plan_id),
                    status TEXT DEFAULT 'pending',
                    payment_receipt TEXT,
                    vpn_config TEXT,
                    admin_note TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # جدول لاگ‌ها
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    log_id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    action TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # ایجاد کاربر ادمین اصلی
            admin_id = int(os.getenv('ADMIN_ID'))
            await conn.execute('''
                INSERT INTO users (user_id, is_admin, balance)
                VALUES ($1, TRUE, 0)
                ON CONFLICT (user_id) DO UPDATE SET is_admin = TRUE
            ''', admin_id)
            
            # ایجاد پلن‌های پیش‌فرض
            await conn.execute('''
                INSERT INTO plans (name, price, duration_days, description) 
                VALUES 
                ('پلن یک ماهه', 29000, 30, 'دسترسی یک ماهه به VPN پرسرعت'),
                ('پلن سه ماهه', 79000, 90, 'دسترسی سه ماهه با قیمت ویژه'),
                ('پلن یک ساله', 199000, 365, 'دسترسی یک ساله با بهترین قیمت')
                ON CONFLICT DO NOTHING
            ''')
    
    # متدهای مدیریت کاربران
    async def get_user(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
    
    async def create_user(self, user_id: int, username: str, first_name: str, last_name: str = ""):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (user_id) DO NOTHING
            ''', user_id, username, first_name, last_name)
    
    async def update_balance(self, user_id: int, amount: int):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                UPDATE users SET balance = balance + $1 WHERE user_id = $2
            ''', amount, user_id)
    
    # متدهای مدیریت پلن‌ها
    async def get_plans(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('SELECT * FROM plans WHERE is_active = TRUE ORDER BY price')
    
    async def get_plan(self, plan_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM plans WHERE plan_id = $1', plan_id)
    
    # متدهای مدیریت سفارشات
    async def create_order(self, user_id: int, plan_id: int) -> int:
        async with self.pool.acquire() as conn:
            return await conn.fetchval('''
                INSERT INTO orders (user_id, plan_id) 
                VALUES ($1, $2) 
                RETURNING order_id
            ''', user_id, plan_id)
    
    async def get_user_orders(self, user_id: int):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT o.*, p.name as plan_name, p.price 
                FROM orders o 
                JOIN plans p ON o.plan_id = p.plan_id 
                WHERE o.user_id = $1 
                ORDER BY o.created_at DESC
            ''', user_id)
    
    async def update_order_status(self, order_id: int, status: str, vpn_config: str = None, admin_note: str = None):
        async with self.pool.acquire() as conn:
            query = 'UPDATE orders SET status = $1, updated_at = NOW()'
            params = [status]
            
            if vpn_config:
                query += ', vpn_config = $2'
                params.append(vpn_config)
            if admin_note:
                query += ', admin_note = $3'
                params.append(admin_note)
            
            query += ' WHERE order_id = $4'
            params.append(order_id)
            
            await conn.execute(query, *params)
    
    async def get_pending_orders(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT o.*, u.username, u.first_name, p.name as plan_name, p.price
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                JOIN plans p ON o.plan_id = p.plan_id
                WHERE o.status = 'pending'
                ORDER BY o.created_at DESC
            ''')
    
    # متدهای مدیریت لاگ
    async def add_log(self, user_id: int, action: str, details: str = ""):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO logs (user_id, action, details)
                VALUES ($1, $2, $3)
            ''', user_id, action, details)
    
    # متدهای پنل ادمین
    async def get_all_users(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT u.*, COUNT(o.order_id) as order_count
                FROM users u
                LEFT JOIN orders o ON u.user_id = o.user_id
                GROUP BY u.user_id
                ORDER BY u.created_at DESC
            ''')
    
    async def get_all_orders(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT o.*, u.username, u.first_name, p.name as plan_name, p.price
                FROM orders o
                JOIN users u ON o.user_id = u.user_id
                JOIN plans p ON o.plan_id = p.plan_id
                ORDER BY o.created_at DESC
            ''')
    
    async def get_logs(self, limit: int = 100):
        async with self.pool.acquire() as conn:
            return await conn.fetch(f'''
                SELECT l.*, u.username, u.first_name
                FROM logs l
                LEFT JOIN users u ON l.user_id = u.user_id
                ORDER BY l.created_at DESC
                LIMIT {limit}
            ''')

# ایجاد نمونه global از دیتابیس
db = Database()
