from fastapi import APIRouter, Query, HTTPException, Body
from schemas.doccontrol import (
    GetInfoUser
)
from service.doccontrol import DocService
from typing import Optional, List, Literal


router = APIRouter(prefix="/doccontrol", tags=["Контроль писем"])

@router.post("/user")
async def get_controls(params: GetInfoUser):
    docservice = DocService()
    result = await docservice.get_docs_controls(params.dict())
    return result

@router.post("/user_wo")
async def get_wo_controls(params: GetInfoUser):
    docservice = DocService()
    result = await docservice.get_docs_wo_controls(params.dict())
    return result

