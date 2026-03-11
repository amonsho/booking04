import asyncio
from fastapi import FastAPI
from app.db.database import engine, Base
from app.models import user, room, booking
from app.api.hotel_router import hotel as hotel_router

app = FastAPI()
app.include_router(hotel_router)

@app.on_event("startup")
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def root():
    return {"message": "Booking API"}