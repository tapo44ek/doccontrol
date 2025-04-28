from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.router import router
from db import connect_to_db, close_db_connection

app = FastAPI()

@app.on_event("startup")
async def startup():
    await connect_to_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db_connection()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD", "TRACE", "CONNECT"],
    allow_headers=["*"],
)

app.include_router(router)