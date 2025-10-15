import asyncpg

async def init_db(database_url: str):
    pool = await asyncpg.create_pool(dsn=database_url)
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT PRIMARY KEY,
            is_admin BOOLEAN DEFAULT FALSE
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            action TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
    return pool

async def register_user(pool, user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("""
        INSERT INTO users (id) VALUES ($1)
        ON CONFLICT (id) DO NOTHING;
        """, user_id)

async def is_admin(pool, user_id: int):
    async with pool.acquire() as conn:
        result = await conn.fetchrow("SELECT is_admin FROM users WHERE id=$1", user_id)
        return result and result['is_admin']

async def add_log(pool, user_id: int, action: str):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO logs (user_id, action) VALUES ($1, $2)", user_id, action)
