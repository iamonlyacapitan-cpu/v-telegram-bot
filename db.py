import asyncpg

async def get_pool(dsn):
    return await asyncpg.create_pool(dsn)

async def init_db(pool):
    # ساخت جداول در صورت عدم وجود
    await pool.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id BIGINT PRIMARY KEY,
        is_admin BOOLEAN DEFAULT FALSE
    )
    """)
    await pool.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        status TEXT
    )
    """)
    await pool.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        action TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
    """)
