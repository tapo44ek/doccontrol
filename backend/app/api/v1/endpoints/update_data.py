from fastapi import APIRouter, Query, HTTPException, Body, Request
import requests
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
    force = request.query_params.get("force") == "true"
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    dataservice = DataService()
    result = await dataservice.run_update_data_and_wait({"user_id": uuid, "force": force})
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
    params = request.query_params
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    docrepository = DocRepository()
    if not params.get("id"):
        raise HTTPException(status_code=400, detail="id обновления выгрузок отсутствует в запросе")
    
    result = await docrepository.get_env_status(int(params.get("id")))
    return result

@router.patch("/docs_by_id")
async def update_docs_by_id(request: Request, params: UpdateDocs):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    print(params)
    params_dict = params.dict()
    params_dict['user_id'] = uuid
    try:
        # response = requests.get("https://dsa.mlc.gov/auth_api/v1/user/get_subordinates", cookies=request.cookies)
        response = requests.get("http://10.9.96.160:5153/v1/user/get_subordinates", cookies=request.cookies)
        print(response)
        if response.ok:
            data = response.json()
            print(data)
            if data is None:
                subordinates = []
            else:
                subordinates = data.get('subordinates', [])
        elif response.status_code == 401:
            raise HTTPException(401, detail='Auth token is incorrect')
        else:
            subordinates = []
            
    except Exception as e:
        print(e)
        subordinates = []
    params_dict['subordinates'] = subordinates
    dataservice = DataService()
    result = await dataservice.run_update_list_docs(params_dict)
    return result