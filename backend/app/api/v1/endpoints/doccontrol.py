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

