import psycopg2
import pandas as pd
from config import ProjectManagementSettings
from pprint import pprint
import json

params = {
    "executor_name": "Габитов Д.Ш.",
    "executor_sedo_id": 78264321,
    "boss1_name": "Мусиенко О.А.",
    "boss1_sedo_id": 70045,
    "boss2_name": "Биктимиров Р.Г.",
    "boss2_sedo_id": 78164285,
    "boss3_name": "Гаман М.Ф.",
    "boss3_sedo_id": 1558294
}

with open("./sql/select_placeholders.sql", "r", encoding="utf-8") as f:
    sql_template = f.read()


sql = (
    sql_template
    .replace("__EXECUTOR_NAME__", f'"{params["executor_name"]}"')
    .replace("__EXECUTOR_SEDO_ID__", str(params["executor_sedo_id"]))
    .replace("__BOSS1_NAME__", f'"{params["boss1_name"]}"')
    .replace("__BOSS1_SEDO_ID__", str(params["boss1_sedo_id"]))
    .replace("__BOSS2_NAME__", f'"{params["boss2_name"]}"')
    .replace("__BOSS2_SEDO_ID__", str(params["boss2_sedo_id"]))
    .replace("__BOSS3_NAME__", f'"{params["boss3_name"]}"')
    .replace("__BOSS3_SEDO_ID__", str(params["boss3_sedo_id"]))
)

with psycopg2.connect(
            host=ProjectManagementSettings.DB_HOST,
            user=ProjectManagementSettings.DB_USER,
            password=ProjectManagementSettings.DB_PASSWORD,
            port=ProjectManagementSettings.DB_PORT,
            database=ProjectManagementSettings.DB_NAME
        ) as conn:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()

# ✅ Результат как list[dict] (для фронта или API)
result_dicts = [dict(zip(colnames, row)) for row in rows]

# ✅ В JSON (например для FastAPI)
result_json = json.dumps(result_dicts, ensure_ascii=False, default=str)
pprint(result_json)

# ✅ В DataFrame (для Excel)
df = pd.DataFrame(result_dicts)

# Сохраняем в Excel (если нужно)
df.to_excel(f"./test_docs/результаты_{params['executor_name']}.xlsx", index=False)