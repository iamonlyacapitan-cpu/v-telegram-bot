import asyncpg

async def create_pool(database_url):
    return await asyncpg.create_pool(dsn=database_url)

async def register_user(pool, user_id: int):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users(id) 
            VALUES($1)
            ON CONFLICT (id) DO NOTHING
        """, user_id)

async def is_admin(pool, user_id: int) -> bool:
    async with pool.acquire() as conn:
        result = await conn.fetchval("SELECT is_admin FROM users WHERE id=$1", user_id)
        return result is True

async def add_log(pool, user_id: int, action: str):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO logs(user_id, action)
            VALUES($1, $2)
        """, user_id, action)
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    action TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
