import asyncpg
from db import get_connection
from pathlib import Path


class DocRepository:
    SQL_PATH = Path("./sql/asyncpg_flat_controls.sql")

    async def get_doc_controls(self, params: dict) -> list[dict]:
        sql_template = self.SQL_PATH.read_text(encoding="utf-8")
        query_params = [
            f'$[*] ? (@.person == "{params["name"]}" && @.closed_date == null)',  # $1
            f'$[*] ? (@.sedo_id == "{params["sedo_id"]}")',                          # $2
            f'$[*] ? (@.author like_regex "{params["name"]}")',                    # $3
            f'$[*] ? (@.sedo_id == "{params["boss1_sedo"]}")',                              # $4
            f'$[*] ? (@.sedo_id == "{params["boss2_sedo"]}")',                              # $5
            f'$[*] ? (@.sedo_id == "{params["boss3_sedo"]}")',                              # $6
            params["name"],                                                       # $7
            params["boss1_name"],                                                          # $8
            params["boss2_name"],                                                          # $9
            params["boss3_name"],                                                         # $10
            int(params["sedo_id"])                                               # $11 (author_id)
        ]

        print(query_params)
        async with get_connection() as conn:
            stmt = await conn.prepare(sql_template)
            rows = await stmt.fetch(*query_params)
        
        return [dict(row) for row in rows]

    
    # def get_docs_to_update(self):
        
    #     return


