from pydantic import BaseModel

class SedoIdsRequest(BaseModel):
    executor_sedo_id: str
    boss1_sedo_id: str
    boss2_sedo_id: str
    boss3_sedo_id: str

class GetInfoUser(BaseModel):
    user_id: int

class UpdateDocs(BaseModel):
    doclist: list