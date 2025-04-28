import asyncpg
from fastapi import FastAPI
from core.config import ProjectManagementSettings

pool: asyncpg.Pool = None

async def connect_to_db():
    global pool
    pool = await asyncpg.create_pool(
        host=ProjectManagementSettings.DB_HOST,
        port=ProjectManagementSettings.DB_PORT,
        user=ProjectManagementSettings.DB_USER,
        password=ProjectManagementSettings.DB_PASSWORD,
        database=ProjectManagementSettings.DB_NAME,
        min_size=5,
        max_size=20,
    )

async def close_db_connection():
    await pool.close()

def get_pool():
    return pool

def get_connection():
    return pool.acquire()