from fastapi import APIRouter, Query, HTTPException, Body, Request
from schemas.doccontrol import (
    GetInfoUser
)
from service.doccontrol import DocService
from typing import Optional, List, Literal
import requests


router = APIRouter(prefix="/doccontrol", tags=["Контроль писем"])

@router.get("/user")
async def get_controls(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    docservice = DocService()

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
            subordinates = [0]
    except Exception as e:
        print(e)
        subordinates = []
    
    result = await docservice.get_docs_controls({'user_id': uuid, "subordinates": subordinates})
    return result

# @router.get("/user")
# async def get_controls(request: Request):
#     uuid = request.cookies.get("uuid")
#     if not uuid:
#         raise HTTPException(status_code=401, detail="uuid не найден")
#     docservice = DocService()

#     result = await docservice.get_docs_controls({'user_id': uuid})
#     return result

@router.get("/user_wo")
async def get_wo_controls(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    docservice = DocService()

    try:
        # response = requests.get("https://dsa.mlc.gov/auth_api/v1/user/get_subordinates", cookies=request.cookies)
        response = requests.get("http://10.9.96.160:5153/v1/user/get_subordinates", cookies=request.cookies)
        print(response)
        if response.ok:
            data = response.json()
            print(data)
            subordinates = data.get('subordinates', [0])
        elif response.status_code == 401:
            raise HTTPException(401, detail='Auth token is incorrect')
        else:
            subordinates = [0]
    except Exception as e:
        print(e)
        subordinates = [0]
    result = await docservice.get_docs_wo_controls({'user_id': uuid, "subordinates": subordinates})
    return result

@router.get("/boss_names")
async def get_boss_names(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    docservice = DocService()
    result = await docservice.get_boss_names({'user_id': uuid})
    return result



