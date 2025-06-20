import asyncpg
from db import get_connection
from pathlib import Path
from core.config import ProjectManagementSettings
import psycopg2
from fastapi import HTTPException
from datetime import datetime, timedelta
from pprint import pprint
import json


class DocRepository:
    SQL_PATH = Path("./sql/asyncpg_flat_controls.sql")
    SQL_PATH_WO_CONTROL = Path("./sql/asyncpg_flat_wo_controls.sql")
    SQL_PATH_DOC_LIST = Path("./sql/asyncpg_flat_controls_doclist.sql")

    async def get_doc_controls(self, params: dict) -> list[dict]:
        sql_template = self.SQL_PATH.read_text(encoding="utf-8")
        query_params = [
            f'$[*] ? (@.person == "{params["name"]}" && @.closed_date == null)',                                         # $1
            f'$[*] ? (@.sedo_id == "{params["sedo_id"]}")',                                                              # $2
            f'$[*] ? (@.author like_regex "{params["name"]}")',                                                          # $3
            f'$[*] ? (@.sedo_id == "{params["sedo_id"]}")',                                                              # $4
            f'$[*] ? (@.author like_regex "{params["name"]}")',                                                          # $5
            f'$[*] ? (@.person == "{params["name"]}" && @.due_date != null)',                                            # $6
            f'$[*] ? (@.sedo_id == "{params["boss1_sedo"]}")',                                                           # $7
            f'$[*] ? (@.sedo_id == "{params["boss2_sedo"]}")',                                                           # $8
            f'$[*] ? (@.sedo_id == "{params["boss3_sedo"]}")',                                                           # $9
            params["name"],                                                                                              # $10
            params["boss1_name"],                                                                                        # $11
            params["boss2_name"],                                                                                        # $12
            params["boss3_name"],                                                                                        # $13
            int(params["sedo_id"]),                                                                                      # $14 (author_id)
            params["subordinate_sedo_ids"]                                                                               # $15 (employee ids)
        ]

        pprint(query_params)
        async with get_connection() as conn:
            stmt = await conn.prepare(sql_template)
            rows = await stmt.fetch(*query_params)
        
        return [dict(row) for row in rows]

    async def get_env_status(self):
        query = '''
            SELECT is_working, user_uuid
            FROM public.env
            WHERE id = 1
            ORDER BY id ASC
            LIMIT 1;
        '''
        async with get_connection() as conn:
            row = await conn.fetchrow(query)
            try:
                if row is not None:
                    print(row)
                    return row  # тип bool: True / False
                else:
                    raise  HTTPException(status_code=404, detail='smth wrong with database, env for updating not found') # если записи нет
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                

    async def get_docs_by_id(self, params: dict) -> list[dict]:
        sql_template = self.SQL_PATH_DOC_LIST.read_text(encoding="utf-8")
        query_params = [
            f'$[*] ? (@.person == "{params["name"]}" && @.closed_date == null)',  # $1
            f'$[*] ? (@.sedo_id == "{params["sedo_id"]}")',                          # $2
            params['doclist'],                    # $3
            f'$[*] ? (@.sedo_id == "{params["boss1_sedo"]}")',                              # $4
            f'$[*] ? (@.sedo_id == "{params["boss2_sedo"]}")',                              # $5
            f'$[*] ? (@.sedo_id == "{params["boss3_sedo"]}")',                              # $6
            params["name"],                                                       # $7
            params["boss1_name"],                                                          # $8
            params["boss2_name"],                                                          # $9
            params["boss3_name"],                                                         # $10
            int(params["sedo_id"]),                                               # $11 (author_id)
            params["subordinate_sedo_ids"]                                           # $11 (author_id)
        ]

        print(query_params)
        async with get_connection() as conn:
            stmt = await conn.prepare(sql_template)
            rows = await stmt.fetch(*query_params)
        
        return [dict(row) for row in rows]  


    async def get_doc_wo_controls(self, params: dict) -> list[dict]:
        sql_template = self.SQL_PATH_WO_CONTROL.read_text(encoding="utf-8")
        query_params = [
            f'$[*] ? (@.sedo_id == "{params["sedo_id"]}")',   # $1
            f'$[*] ? (@.author like_regex "{params["name"]}")',                          # $2
            f'$[*] ? (@.person == "{params["name"]}" && @.due_date != null && @.closed_date == null)',                   # $3
            f'$[*] ? (@.sedo_id == "{params["boss1_sedo"]}")',                              # $4
            f'$[*] ? (@.sedo_id == "{params["boss2_sedo"]}")',                              # $5
            f'$[*] ? (@.sedo_id == "{params["boss3_sedo"]}")',                              # $6
            params["name"],                                                       # $7
            params["boss1_name"],                                                          # $8
            params["boss2_name"],                                                          # $9
            params["boss3_name"],                                                         # $10
            int(params["sedo_id"]),                                               # $11 (author_id)
            params["subordinate_sedo_ids"]                                               # $11 (author_id)
        ]

        print(query_params)
        async with get_connection() as conn:
            stmt = await conn.prepare(sql_template)
            rows = await stmt.fetch(*query_params)
        
        return [dict(row) for row in rows]


    def get_docs_to_update(self, params :dict) -> None | dict:

        if params['force']:  ## True для "короткого" обновления
            print('DB FORCE')
            print( {(datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')})
            print({(datetime.now().date() + timedelta(days=2)).strftime('%Y-%m-%d')})
            sql = f'''
            SELECT DISTINCT doc_id
            FROM (
                SELECT f.doc_id
                FROM public.flat_resolution f
                WHERE jsonb_path_exists(
                    f.recipients,
                    '$[*] ? (@.sedo_id == "{params["sedo_id"]}")'
                )
                AND jsonb_path_exists(
                    f.controls,
                      '$[*] ? (
                        @.person == $name &&
                        @.due_date != null &&
                        @.closed_date == null &&
                        @.due_date >= $from_date &&
                        @.due_date <= $to_date
                    )',
                    jsonb_build_object(
                    'name', to_jsonb('{str(params['name'])}' ::text),
                    'from_date', to_jsonb('{(datetime.now().date() - timedelta(days=1)).strftime('%Y-%m-%d')}' :: date),
                    'to_date', to_jsonb('{(datetime.now().date() + timedelta(days=2)).strftime('%Y-%m-%d')}' :: date)
                    )
                )
                );
        '''
            print(sql)
        else:
            sql = f'''
                SELECT DISTINCT doc_id
                FROM (
                    SELECT f.doc_id
                    FROM public.flat_resolution f
                    WHERE jsonb_path_exists(
                        f.recipients,
                        '$[*] ? (@.sedo_id == "{params["sedo_id"]}")'
                    )
                    AND jsonb_path_exists(
                        f.controls,
                        '$[*] ? (@.person == "{params["name"]}" && @.due_date != null && @.closed_date == null)'
                    )

                    UNION

                    SELECT f.doc_id
                    FROM public.flat_resolution f
                    WHERE jsonb_path_exists(
                        f.recipients,
                        '$[*] ? (@.sedo_id == "{params["sedo_id"]}")'
                    )
                    AND NOT jsonb_path_exists(
                        f.executions,
                        '$[*] ? (@.author == "{params["name"]}")'
                    )
                    AND NOT jsonb_path_exists(
                        f.controls,
                        '$[*] ? (@.person == "{params["name"]}" && @.due_date != null && @.closed_date == null)'
                    )
                ) AS combined;
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

            rows = cursor.fetchall()
            if rows:
                return [row[0] for row in rows]
            else: return []

        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
        finally:
            cursor.close()
            connection.close()
        
        return result

    def get_sogl_to_update(self, params :dict) -> None | dict:

        sql = f'''
            SELECT DISTINCT sedo_id
            FROM public.sogly
            where registered_sedo_id is NULL;
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

            rows = cursor.fetchall()
            if rows:
                return [row[0] for row in rows]
            else: return []

        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
        finally:
            cursor.close()
            connection.close()
        return result

    def get_sogl_from_docs_to_update(self, params :dict) -> None | dict:
        sql = f'''
                SELECT 
                    (elem->>'project_id')::int AS sogl_id
                FROM public.documents AS a
                JOIN LATERAL jsonb_array_elements(a.projects) AS elem ON TRUE
                INNER JOIN (
                    SELECT DISTINCT doc_id
                    FROM (
                        SELECT f.doc_id
                        FROM public.flat_resolution f
                        WHERE jsonb_path_exists(
                            f.recipients,
                            '$[*] ? (@.sedo_id == "{params["sedo_id"]}")'
                        )
                        AND jsonb_path_exists(
                            f.controls,
                            '$[*] ? (@.person == "{params["name"]}" && @.due_date != null && @.closed_date == null)'
                        )

                        UNION

                        SELECT f.doc_id
                        FROM public.flat_resolution f
                        WHERE jsonb_path_exists(
                            f.recipients,
                            '$[*] ? (@.sedo_id == "{params["sedo_id"]}")'
                        )
                        AND NOT jsonb_path_exists(
                            f.executions,
                            '$[*] ? (@.author == "{params["name"]}")'
                        )
                        AND NOT jsonb_path_exists(
                            f.controls,
                            '$[*] ? (@.person == "{params["name"]}" && @.due_date != null && @.closed_date == null)'
                        )
                    ) AS combined
                ) combined_docs ON a.sedo_id = combined_docs.doc_id;   

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

            rows = cursor.fetchall()
            if rows:
                return [row[0] for row in rows]
            else: return []

        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
        finally:
            cursor.close()
            connection.close()
        return result

