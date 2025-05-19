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
        if id is None:
            return None
        async with get_connection() as conn:
            row = await conn.fetchrow(sql, id)
        
        if row:
            return row['name']
        return "Not Found"

    
    async def get_user_info_by_id(self, id :int) -> dict | None:
        
        sql = '''
        SELECT sedo_id, name, boss1_sedo, boss2_sedo, boss3_sedo, start_d_days, end_d_days 
        FROM public.user 
        WHERE uuid = $1 
        LIMIT 1
        '''
        try:
            async with get_connection() as conn:
                row = await conn.fetchrow(sql, id)
        
            if row:
                return dict(row)
            return None

        except Exception as e:
            raise HTTPException(status_code=500, detail=e)

    def no_pool_get_user_info_by_id(self, id :str) -> dict | None:
        
        sql = f'''
        SELECT sedo_id, name, boss1_sedo, boss2_sedo, boss3_sedo, start_d_days, end_d_days 
        FROM public.user 
        WHERE uuid = '{id}' 
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
            colnames = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            if rows:
                print(rows)
                print(type(rows))
                return dict(zip(colnames, rows[0]))
            else: return None

        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
        finally:
            cursor.close()
            connection.close()
        return result


    def no_pool_get_user_fio_by_sedo_id(self, id :int) -> str:
        
        if id is None:
            return None
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
