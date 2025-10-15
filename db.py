import asyncpg
import datetime

from config import DATABASE_URL

async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

async def init_db(pool):
    async with pool.acquire() as conn:
        # Users
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            wallet BIGINT DEFAULT 0,
            created_at TIMESTAMP
        )
        """)
        # Admins
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS admins(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            added_at TIMESTAMP
        )
        """)
        # Plans
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS plans(
            id SERIAL PRIMARY KEY,
            name TEXT,
            price BIGINT,
            description TEXT
        )
        """)
        # Orders
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
        )
        """)
        # Settings
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)
        # Logs
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS logs(
            id SERIAL PRIMARY KEY,
            actor_id BIGINT,
            action TEXT,
            created_at TIMESTAMP
        )
        """)
        # Default bank info
        await conn.execute("""
        INSERT INTO settings(key,value) VALUES('bank_info','6037-9912-3456-7890 به نام پینگ‌من')
        ON CONFLICT (key) DO NOTHING
        """)
        # Initial admin
        from config import ADMIN_ID
        await conn.execute("""
        INSERT INTO admins(telegram_id, added_at) VALUES($1, $2)
        ON CONFLICT (telegram_id) DO NOTHING
        """, ADMIN_ID, datetime.datetime.now())

# Helper DB functions
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

# Plan functions
async def get_all_plans(pool):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM plans ORDER BY id")

async def add_plan(pool, name, price, description):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO plans(name,price,description) VALUES($1,$2,$3)", name, price, description)

async def delete_plan(pool, plan_id):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM plans WHERE id=$1", plan_id)

# Order functions
async def get_all_orders(pool):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM orders ORDER BY created_at DESC")

async def update_order_status(pool, order_id, status):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE orders SET status=$1 WHERE id=$2", status, order_id)

async def set_order_config(pool, order_id, config_text):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE orders SET config_text=$1 WHERE id=$2", config_text, order_id)
