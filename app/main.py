import asyncio
from fastapi import FastAPI
from app.db.database import engine, Base

from app.models import user, room, booking
from app.api.hotel_router import hotel as hotel_router

from app.models import user, room, booking, hotel


app = FastAPI()
app.include_router(hotel_router)

@app.on_event("startup")
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from app.api.auth_router import router as auth_router
from app.api.user_router import router as user_router
from app.api.profile_router import router as profile_router

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(profile_router)

from fastapi.staticfiles import StaticFiles
app.mount("/media", StaticFiles(directory="media"), name="media")
