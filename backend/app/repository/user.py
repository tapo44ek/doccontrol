import asyncpg
from db import get_connection
from fastapi import HTTPException
from pathlib import Path
from core.config import ProjectManagementSettings
import psycopg2


class UserRepository:
    async def get_user_fio_by_sedo_id(self, id :int) -> str:

        sql = '''
        SELECT name 
        FROM catalog.sedo 
        WHERE sedo_id = $1 
        LIMIT 1
        '''

        async with get_connection() as conn:
            row = await conn.fetchrow(sql, id)
        
        if row:
            return row['name']
        return "Not Found"

    def no_pool_get_user_fio_by_sedo_id(self, id :int) -> str:

        sql = f'''
        SELECT name 
        FROM catalog.sedo 
        WHERE sedo_id = {int(id)} 
        LIMIT 1
        '''
        connection = psycopg2.connect(
            host=ProjectManagementSettings.DB_HOST,
            user=ProjectManagementSettings.DB_USER,
            password=ProjectManagementSettings.DB_PASSWORD,
            port=ProjectManagementSettings.DB_PORT,
            database=ProjectManagementSettings.DB_NAME
        )
        cursor = connection.cursor()

        try:
            cursor.execute(sql)

            row = cursor.fetchone()
            if row:
                return row[0]
            else: return "NOT FOUND"

        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
        finally:
            cursor.close()
            connection.close()
        return result
