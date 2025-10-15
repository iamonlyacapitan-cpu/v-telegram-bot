import asyncpg

# ایجاد کانکشن پول
async def get_pool(database_url):
    return await asyncpg.create_pool(database_url)

# ایجاد جداول اگر نبود
async def init_db(database_url):
    pool = await get_pool(database_url)
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            action TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            user_id BIGINT PRIMARY KEY,
            balance NUMERIC DEFAULT 0
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            plan TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)
    print("Database initialized.")
    return pool

# فانکشن‌های کاربردی
async def register_user(pool, user_id):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users(id) VALUES($1) ON CONFLICT DO NOTHING
        """, user_id)

async def is_admin(pool, user_id):
    return str(user_id) == os.environ.get("ADMIN_ID")

async def add_log(pool, user_id, action):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO logs(user_id, action) VALUES($1, $2)
        """, user_id, action)
