from fastapi import APIRouter, Query, HTTPException, Body
from schemas.update_data import (
    SedoUpdate
)
from schemas.doccontrol import GetInfoUser, UpdateDocs
from service.update_data import DataService
from typing import Optional, List, Literal


router = APIRouter(prefix="/update", tags=["Обновление"])

@router.patch("/user")
async def get_controls(params: GetInfoUser):
    dataservice = DataService()
    result = await dataservice.run_update_data_and_wait(params.dict())
    return result

@router.patch("/docs_by_id")
async def update_docs_by_id(params: UpdateDocs):
    dataservice = DataService()
    result = await dataservice.run_update_list_docs(params.dict())
    return result