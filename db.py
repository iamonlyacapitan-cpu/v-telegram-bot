import asyncpg

# Pool برای اتصال دیتابیس
async def get_pool(dsn):
    return await asyncpg.create_pool(dsn)

# ساخت جداول اولیه
async def init_db(pool):
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

# توابع مورد نیاز handlers
async def register_user(pool, user_id):
    await pool.execute("""
    INSERT INTO users(id) VALUES($1)
    ON CONFLICT (id) DO NOTHING
    """, user_id)

async def is_admin(pool, user_id):
    result = await pool.fetchrow("SELECT is_admin FROM users WHERE id=$1", user_id)
    return result and result['is_admin']

async def add_log(pool, user_id, action):
    await pool.execute("INSERT INTO logs(user_id, action) VALUES($1, $2)", user_id, action)
