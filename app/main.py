import asyncio
from fastapi import FastAPI
from app.db.database import engine, Base
from app.models import user, room, booking, hotel

app = FastAPI()

@app.on_event("startup")
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from app.api.auth_router import router as auth_router

app.include_router(auth_router)