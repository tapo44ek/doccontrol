from pydantic import BaseModel

class SedoUpdate(BaseModel):
    date_from: str
    date_to: str
    sedo_id: int