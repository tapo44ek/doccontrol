import asyncpg
import psycopg2
from psycopg2.extras import execute_values
from config import ProjectManagementSettings
from db import get_connection
from datetime import datetime
from pathlib import Path
import json
from fastapi import HTTPException
from dateutil.parser import isoparse

class SedoData:

    async def set_env_update_on(self, uuid: str):
        query_env = '''
            UPDATE public.env
            SET
                is_working = TRUE,         -- или FALSE, если нужно
                user_uuid = $1,
                updated_at = NOW()
            WHERE
                id = 1;    
        '''

        query_history = '''
        INSERT INTO public.history (env_id, user_uuid, started_at)
        VALUES (1, $1, NOW());
        '''

        try:
            async with get_connection() as conn:
                async with conn.transaction():
                    await conn.execute(query_env, uuid)
        except Exception as e:
            raise HTTPException(500, detail=f"set env error: {str(e)}")

        try:
            async with get_connection() as conn:
                async with conn.transaction():
                    await conn.execute(query_history, uuid)
        except Exception as e:
            raise HTTPException(500, detail=f"insert history error: {str(e)}")
        
        return {'status_code': '200', 'detail': 'success'}


    async def set_env_update_off(self, uuid: str):
        query_env = '''
            UPDATE public.env
            SET
                is_working = FALSE,         -- или FALSE, если нужно
                user_uuid = NULL,
                updated_at = NOW()
            WHERE
                id = 1;    
        '''

        query_history = '''
            UPDATE public.history
            SET finished_at = NOW()
            WHERE id = (
                SELECT id
                FROM public.history
                WHERE user_uuid = $1
                AND finished_at IS NULL
                ORDER BY started_at DESC
                LIMIT 1
            );
        '''

        try:
            async with get_connection() as conn:
                async with conn.transaction():
                    await conn.execute(query_env)
        except Exception as e:
            raise HTTPException(500, detail=f"unset env error: {str(e)}")

        try:
            async with get_connection() as conn:
                async with conn.transaction():
                    await conn.execute(query_env)
                    if uuid:
                        await conn.execute(query_history, uuid)

        except Exception as e:
            raise HTTPException(500, detail=f"update history error: {str(e)}")

        return {'status_code': '200', 'detail': 'success'}


    async def as_insert_resolutions_into_db(self, data: list):

        rows = []
        for item in data:
            row = (
                item['id'],
                item.get('parent_id'),
                item['doc_id'],
                int(item['author_id']) if item.get('author_id') not in (None, '',) else None,
                isoparse(item['date']),
                item['dl'],
                item['type'],
                json.dumps(item.get('controls', []), ensure_ascii=False),
                json.dumps(item.get('executions', []), ensure_ascii=False),
                json.dumps(item.get('recipients', []), ensure_ascii=False)
            )
            rows.append(row)

        query = """
            INSERT INTO public.flat_resolution (
                id, parent_id, doc_id, author_id, date, dl, type,
                controls, executions, recipients
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (id) DO UPDATE SET
                parent_id = EXCLUDED.parent_id,
                doc_id = EXCLUDED.doc_id,
                author_id = EXCLUDED.author_id,
                date = EXCLUDED.date,
                dl = EXCLUDED.dl,
                type = EXCLUDED.type,
                controls = EXCLUDED.controls,
                executions = EXCLUDED.executions,
                recipients = EXCLUDED.recipients,
                updated_at = NOW()
        """            

        try:
            async with get_connection() as conn:
                async with conn.transaction():
                    await conn.executemany(query, rows)
            return 'success'
        except Exception as e:
            raise HTTPException(500, detail=e)


    async def as_insert_docs_into_db(self, data: dict):

        query = """
            INSERT INTO documents (
                sedo_id, date, dgi_number, description,
                executor_id, executor_fio, executor_company,
                signed_by_id, signed_by_fio, signed_by_company,
                answer, recipients
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            ON CONFLICT (sedo_id) DO UPDATE SET
                date = EXCLUDED.date,
                dgi_number = EXCLUDED.dgi_number,
                description = EXCLUDED.description,
                executor_id = EXCLUDED.executor_id,
                executor_fio = EXCLUDED.executor_fio,
                executor_company = EXCLUDED.executor_company,
                signed_by_id = EXCLUDED.signed_by_id,
                signed_by_fio = EXCLUDED.signed_by_fio,
                signed_by_company = EXCLUDED.signed_by_company,
                answer = EXCLUDED.answer,
                recipients = EXCLUDED.recipients,
                updated_at = NOW()
        """

        params = (
            data['sedo_id'],
            datetime.strptime(data['date'], "%d.%m.%Y").date(),
            data['dgi_number'],
            data['description'],
            int(data['executor_id']) if data.get('executor_id') not in (None, '',) else None,
            data['executor_fio'],
            data['executor_company'],
            int(data['signed_by_id']) if data.get('signed_by_id') not in (None, '',) else None,
            data['signed_by_fio'],
            data['signed_by_company'],
            json.dumps(data['answer'], ensure_ascii=False),
            json.dumps(data['recipients'], ensure_ascii=False),
        )

        try:
            async with get_connection() as conn:
                async with conn.transaction():
                    await conn.execute(query, *params)
            return 1
        except Exception as e:
            raise HTTPException(500, detail=e)

    def insert_resolutions_into_db(self, data :list):
        connection = psycopg2.connect(
                host=ProjectManagementSettings.DB_HOST,
                user=ProjectManagementSettings.DB_USER,
                password=ProjectManagementSettings.DB_PASSWORD,
                port=ProjectManagementSettings.DB_PORT,
                database=ProjectManagementSettings.DB_NAME
            )
        cursor = connection.cursor()
        doc_ids = set()
        rows = []
        for item in data:
            doc_ids.add(int(item['doc_id']))
            row = (
                item['id'],
                item.get('parent_id'),
                item['doc_id'],
                int(item['author_id']) if (item['author_id'] is not None) & (item['author_id'] != '') else None,
                isoparse(item['date']),
                item['dl'],
                item['type'],
                json.dumps(item.get('controls', []), ensure_ascii=False),
                json.dumps(item.get('executions', []), ensure_ascii=False),
                json.dumps(item.get('recipients', []), ensure_ascii=False)
            )
            rows.append(row)



        try:

            if doc_ids:
                query = "DELETE FROM public.flat_resolution WHERE doc_id = ANY(%s)"
                cursor.execute(query, (list(doc_ids),))

            execute_values(cursor, """
                INSERT INTO public.flat_resolution (
                    id, parent_id, doc_id, author_id, date, dl, type,
                    controls, executions, recipients
                )
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    parent_id = EXCLUDED.parent_id,
                    doc_id = EXCLUDED.doc_id,
                    author_id = EXCLUDED.author_id,
                    date = EXCLUDED.date,
                    dl = EXCLUDED.dl,
                    type = EXCLUDED.type,
                    controls = EXCLUDED.controls,
                    executions = EXCLUDED.executions,
                    recipients = EXCLUDED.recipients,
                    updated_at = NOW()
            """, rows)

            connection.commit()
            result = 1
            return 1
        except Exception as e:
            raise HTTPException(500, detail=e)
        finally:
            cursor.close()
            connection.close()
        return result


    def insert_documents_into_db(self, doc :dict):
        connection = psycopg2.connect(
            host=ProjectManagementSettings.DB_HOST,
            user=ProjectManagementSettings.DB_USER,
            password=ProjectManagementSettings.DB_PASSWORD,
            port=ProjectManagementSettings.DB_PORT,
            database=ProjectManagementSettings.DB_NAME
        )
        cursor = connection.cursor()

        try:
            cursor.execute("""
                INSERT INTO documents (
                    sedo_id, date, dgi_number, description,
                    executor_id, executor_fio, executor_company,
                    signed_by_id, signed_by_fio, signed_by_company,
                    answer, recipients
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sedo_id) DO UPDATE SET
                    date = EXCLUDED.date,
                    dgi_number = EXCLUDED.dgi_number,
                    description = EXCLUDED.description,
                    executor_id = EXCLUDED.executor_id,
                    executor_fio = EXCLUDED.executor_fio,
                    executor_company = EXCLUDED.executor_company,
                    signed_by_id = EXCLUDED.signed_by_id,
                    signed_by_fio = EXCLUDED.signed_by_fio,
                    signed_by_company = EXCLUDED.signed_by_company,
                    answer = EXCLUDED.answer,
                    recipients = EXCLUDED.recipients,
                    updated_at = NOW()
            """, (
                doc['sedo_id'],
                datetime.strptime(doc['date'], "%d.%m.%Y").date(),
                doc['dgi_number'],
                doc['description'],
                int(doc['executor_id']) if (doc['executor_id'] is not None) & (doc['executor_id'] != '') else None,
                doc['executor_fio'],
                doc['executor_company'],
                int(doc['signed_by_id']) if (doc['signed_by_id'] is not None) & (doc['signed_by_id'] != '') else None,
                doc['signed_by_fio'],
                doc['signed_by_company'],
                json.dumps(doc['answer'], ensure_ascii=False),
                json.dumps(doc['recipients'], ensure_ascii=False)
            ))

            connection.commit()
            result = 1
            return 1
        except Exception as e:
            raise HTTPException(500, detail=e)
        finally:
            cursor.close()
            connection.close()
        return result


    def insert_sogly_into_db(self, data :dict):
        connection = psycopg2.connect(
            host=ProjectManagementSettings.DB_HOST,
            user=ProjectManagementSettings.DB_USER,
            password=ProjectManagementSettings.DB_PASSWORD,
            port=ProjectManagementSettings.DB_PORT,
            database=ProjectManagementSettings.DB_NAME
        )
        cursor = connection.cursor()

        values = (
            data["sedo_id"],
            data["dgi_number"],
            datetime.strptime(data["date"], "%d.%m.%Y"),
            data.get("registered_sedo_id"),
            data.get("registered_number"),
            data.get("description"),
            data.get("signed_by_sedo_id"),
            data.get("signed_by_fio"),
            data.get("signed_by_company"),
            data.get("executor_sedo_id"),
            data.get("executor_fio"),
            data.get("executor_company"),
            json.dumps(data.get("answer")),
            json.dumps(data.get("recipients")),
            json.dumps(data.get("structure")),
            datetime.strptime(data.get("started_at"), "%d.%m.%Y %H:%M") if data.get("started_at") != '-' else None
        )

        try:
            cursor.execute("""
                INSERT INTO public.sogly (
                        sedo_id, dgi_number, date,
                        registered_sedo_id, registered_number,
                        description,
                        signed_by_sedo_id, signed_by_fio, signed_by_company,
                        executor_sedo_id, executor_fio, executor_company,
                        answer, recipients, structure,
                        started_at
                    )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (sedo_id) DO UPDATE SET
                    date = EXCLUDED.date,
                    dgi_number = EXCLUDED.dgi_number,
                    description = EXCLUDED.description,
                    registered_sedo_id = EXCLUDED.registered_sedo_id,
                    registered_number = EXCLUDED.registered_number,
                    executor_sedo_id = EXCLUDED.executor_sedo_id,
                    executor_fio = EXCLUDED.executor_fio,
                    executor_company = EXCLUDED.executor_company,
                    signed_by_sedo_id = EXCLUDED.signed_by_sedo_id,
                    signed_by_fio = EXCLUDED.signed_by_fio,
                    signed_by_company = EXCLUDED.signed_by_company,
                    answer = EXCLUDED.answer,
                    recipients = EXCLUDED.recipients,
                    structure = EXCLUDED.structure,
                    updated_at = NOW()
            """, values)

            connection.commit()
            result = 1
            return 1
        except Exception as e:
            raise HTTPException(500, detail=e)
        finally:
            cursor.close()
            connection.close()
        return result

