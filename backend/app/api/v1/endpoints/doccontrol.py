from fastapi import APIRouter, Query, HTTPException, Body, Request
from schemas.doccontrol import (
    GetInfoUser
)
from service.doccontrol import DocService
from typing import Optional, List, Literal


router = APIRouter(prefix="/doccontrol", tags=["Контроль писем"])

@router.get("/user")
async def get_controls(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    docservice = DocService()
    result = await docservice.get_docs_controls({'user_id': uuid})
    return result

@router.get("/user_wo")
async def get_wo_controls(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    docservice = DocService()
    result = await docservice.get_docs_wo_controls({'user_id': uuid})
    return result

@router.get("/boss_names")
async def get_boss_names(request: Request):
    uuid = request.cookies.get("uuid")
    if not uuid:
        raise HTTPException(status_code=401, detail="uuid не найден")
    docservice = DocService()
    result = await docservice.get_boss_names({'user_id': uuid})
    return result



