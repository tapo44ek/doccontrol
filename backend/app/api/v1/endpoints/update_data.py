from fastapi import APIRouter, Query, HTTPException, Body
from schemas.update_data import (
    SedoUpdate
)
from service.update_data import DataService
from typing import Optional, List, Literal


router = APIRouter(prefix="/update", tags=["Обновление"])

@router.patch("/user")
async def get_controls(params: SedoUpdate):
    dataservice = DataService()
    result = await dataservice.run_update_data_and_wait(params.dict())
    return result