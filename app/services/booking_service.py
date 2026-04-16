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

        days = (booking_data.date_to - booking_data.date_from).days
        if days <= 0:
            raise HTTPException(400, "Invalid dates")

        room = await self.repo.get_room_by_id(booking_data.room_id)
        if not room:
            raise HTTPException(404, "Room not found")
        if getattr(room, 'is_available', True) is False:
            raise HTTPException(400, "Room is temporarily unavailable")

        # Check for overlapping dates
        is_overlap = await self.repo.check_overlap(
            booking_data.room_id, 
            booking_data.date_from, 
            booking_data.date_to
        )
        if is_overlap:
            raise HTTPException(400, "Room is already booked for these dates")

        total_price = days * room.price

        new_booking = Booking(
            **booking_data.model_dump(),
            user_id=user_id,
            total_price=total_price
        )
        
        return await self.repo.create_booking(new_booking)

    async def get_user_bookings(self, user_id: int):
        return await self.repo.get_bookings_by_user(user_id)
    
    async def get_deleted_bookings(self):
        return await self.repo.get_deleted_all()
    

    async def delete_booking(self, booking_id: int):
        booking = await self.repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        ok = await self.repo.delete_booking_by_id(booking_id)
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to delete booking")

        return {"message": "Booking deleted successfully", "id": booking_id}

    async def restore_booking(self, booking_id: int):
        booking = await self.repo.restore(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking
    
    
    
    