from api.v1.endpoints.doccontrol import router as doc_router
from api.v1.endpoints.update_data import router as data_router

from fastapi import APIRouter

router = APIRouter()

router.include_router(doc_router)
router.include_router(data_router)
