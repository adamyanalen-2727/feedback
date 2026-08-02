import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432") 

pool: asyncgp.Pool | None = None

async def init_db():
    global pool
    poll = await asyncpg.connect(
            user = DB_USER,
            password = DB_PASSWORD,
            database=DB_NAME,
            host = DB_HOST,
            port = DB_PORT
    )
