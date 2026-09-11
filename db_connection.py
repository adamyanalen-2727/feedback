import asyncio
import asyncpg
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("db_connection")

ADMIN_USER = os.getenv("POSTGRES_USER")
ADMIN_PASSWORD = os.getenv("POSTGRES_PASSWORD")
ADMIN_DB = os.getenv("ADMIN_DB")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
TABLE_NAME = os.getenv("TABLE_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")

# module-level pool, created once
pool: asyncpg.Pool | None = None


async def init_pool():
    """Call this once at startup (e.g. in your bot's on_startup)."""
    global pool
    pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
        min_size=1,
        max_size=10,
    )
    logger.info("DB pool created (min=1, max=5)")



async def close_pool():
    if pool:
        await pool.close()
        logger.info("DB pool closed")

async def get_admin_connection(admin_db):
    """One-off admin connection, used only for provisioning."""
    return await asyncpg.connect(
        user=ADMIN_USER,
        password=ADMIN_PASSWORD,
        database=admin_db,
        host=DB_HOST,
        port=DB_PORT,
    )

async def grant_privileges(conn):
    await conn.execute(
        f'GRANT SELECT, INSERT, UPDATE, DELETE ON {TABLE_NAME} TO "{DB_USER}"'
    )
    await conn.execute(
        f'GRANT USAGE, SELECT ON SEQUENCE {TABLE_NAME}_id_seq TO "{DB_USER}"'
    )
    logger.info(f"Granted privileges on {TABLE_NAME} to {DB_USER}")

async def create_user(conn):
    user_exist = await conn.fetchval(
        "SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname=$1)", DB_USER
    )
    if not user_exist:
        await conn.execute(
            f'CREATE USER "{DB_USER}" WITH PASSWORD $1', DB_PASSWORD
        )
        logger.info(f"Created DB user: {DB_USER}")

async def create_db(conn):
    exist = await conn.fetchval(
        "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=$1)", DB_NAME
    )
    if not exist:
        await conn.execute(f'CREATE DATABASE "{DB_NAME}"')
        logger.info(f"Created database: {DB_NAME}")


async def create_table(conn):
    await conn.execute(
        f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            surname VARCHAR(100),
            stars INTEGER CHECK (stars >= 1 AND stars <= 5),
            message TEXT
        )"""
    )
    logger.info(f"Ensured table exists: {TABLE_NAME}")

async def create_env():
    conn = await get_admin_connection(ADMIN_DB)
    try:
        await create_user(conn)
        await create_db(conn)
    finally:
        await conn.close()

    conn = await get_admin_connection(DB_NAME)
    try:
        await create_table(conn)
        await grant_privileges(conn)  

    finally:
        await conn.close()

async def input_from_telegram(name, surname, stars, message=None):
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {TABLE_NAME}
                (name, surname, stars, message)
                VALUES ($1, $2, $3, $4)
                """,
                name, surname, stars, message
            )
        logger.info(f"Feedback inserted: name={name}, surname={surname}, stars={stars}")
    except Exception:
        logger.exception(f"Failed to insert feedback: name={name}, surname={surname}")
        raise

async def get_feedback():
    async with pool.acquire() as conn:
        rows = await conn.fetch(f"SELECT * FROM {TABLE_NAME} ORDER BY id")
    logger.info(f"Fetched {len(rows)} feedback rows")
    return [dict(row) for row in rows]
