from sqlalchemy import select,func
from fastapi import APIRouter ,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.hotel import Hotel
from app.models.room import Room


report_router = APIRouter(tags=['Report'])


@report_router.get("/reports/hotels_count")
async def hotels_count(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(Hotel.id)))
    count = result.scalar()
    return {"hotels_count": count}