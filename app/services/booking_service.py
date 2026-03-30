from fastapi import APIRouter, Depends, HTTPException ,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.booking import BookingCreate, BookingResponse
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.repositories.booking_repository import BookingRepository
from app.models.booking import Booking

class BookingService:
    def __init__(self, db):
        self.repo = BookingRepository(db)

    async def create_booking(self, booking_data, user_id):

        # 1. дни
        days = (booking_data.date_to - booking_data.date_from).days
        if days <= 0:
            raise HTTPException(400, "Invalid dates")

        # 2. получить room
        room = await self.repo.get_room_by_id(booking_data.room_id)
        if not room:
            raise HTTPException(404, "Room not found")

        # 3. цена
        total_price = days * room.price

        # 4. создать объект
        new_booking = Booking(
            **booking_data.model_dump(),
            user_id=user_id,
            total_price=total_price
        )

        # 5. сохранить
        return await self.repo.create_booking(new_booking)
    