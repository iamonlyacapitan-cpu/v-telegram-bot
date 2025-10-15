import asyncpg
import datetime
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
INITIAL_ADMIN_ID = int(os.environ.get("ADMIN_ID") or 1606291654)

async def create_pool():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL محیطی تنظیم نشده!")
    return await asyncpg.create_pool(DATABASE_URL)

async def init_db(pool):
    async with pool.acquire() as conn:
        # جدول کاربران
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            wallet BIGINT DEFAULT 0,
            created_at TIMESTAMP
        )""")
        # جدول ادمین‌ها
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS admins(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            added_at TIMESTAMP
        )""")
        # جدول پلن‌ها
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS plans(
            id SERIAL PRIMARY KEY,
            name TEXT,
            price BIGINT,
            description TEXT
        )""")
        # جدول سفارش‌ها
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            plan_id INT,
            status TEXT,
            payment_receipt TEXT,
            config_text TEXT,
            config_file_id TEXT,
            reason TEXT,
            created_at TIMESTAMP
        )""")
        # جدول تنظیمات
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        # جدول لاگ
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS logs(
            id SERIAL PRIMARY KEY,
            actor_id BIGINT,
            action TEXT,
            created_at TIMESTAMP
        )""")
        # اطلاعات بانکی پیش‌فرض
        await conn.execute("""
        INSERT INTO settings(key,value) VALUES('bank_info','6037-9912-3456-7890 به نام پینگ‌من')
        ON CONFLICT (key) DO NOTHING
        """)
        # اضافه کردن ادمین اولیه
        await conn.execute("""
        INSERT INTO admins(telegram_id, added_at) VALUES($1, $2)
        ON CONFLICT (telegram_id) DO NOTHING
        """, INITIAL_ADMIN_ID, datetime.datetime.now())

# توابع کمکی
async def register_user(pool, tg_id: int):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO users(telegram_id, created_at) VALUES($1,$2) ON CONFLICT DO NOTHING",
                           tg_id, datetime.datetime.now())

async def is_admin(pool, tg_id: int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT 1 FROM admins WHERE telegram_id=$1", tg_id)
        return bool(row)

async def add_log(pool, actor_id:int, action:str):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO logs(actor_id, action, created_at) VALUES($1,$2,$3)",
                           actor_id, action, datetime.datetime.now())
