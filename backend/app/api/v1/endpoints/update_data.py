from fastapi import APIRouter, Query, HTTPException, Body, Request
from schemas.update_data import (
    SedoUpdate
)
from schemas.doccontrol import GetInfoUser, UpdateDocs
from service.update_data import DataService
from repository.doccontrol import DocRepository
from typing import Optional, List, Literal


router = APIRouter(prefix="/update", tags=["Обновление"])

@router.patch("/all_docs")
async def get_controls(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    dataservice = DataService()
    result = await dataservice.run_update_data_and_wait({"user_id": uuid})
    return result

@router.patch("/all_sogl")
async def get_controls(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    dataservice = DataService()
    result = await dataservice.run_update_sogl_and_wait({"user_id": uuid})
    return result

@router.get("/check_status")
async def get_env_status(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    docrepository = DocRepository()
    result = await docrepository.get_env_status()
    return result

@router.patch("/docs_by_id")
async def update_docs_by_id(request: Request, params: UpdateDocs):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    print(params)
    params_dict = params.dict()
    params_dict['user_id'] = uuid
    dataservice = DataService()
    result = await dataservice.run_update_list_docs(params_dict)
    return result