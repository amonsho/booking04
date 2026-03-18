from fastapi import APIRouter, Depends, HTTPException ,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.booking import BookingCreate, BookingResponse
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.booking import Booking 

class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_booking(self, booking_data:BookingCreate,user_id: int):
        new_booking = Booking(**booking_data.model_dump(),user_id=user_id)
        self.db.add(new_booking)
        await self.db.commit()
        await self.db.refresh(new_booking)
        return new_booking