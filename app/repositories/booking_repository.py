from sqlalchemy import select
from app.models.booking import Booking
from app.models.room import Room 

class BookingRepository:
    def __init__(self, db):
        self.db = db

    async def get_room_by_id(self, room_id: int):
        result = await self.db.execute(
            select(Room).where(Room.id == room_id)
        )
        return result.scalar_one_or_none()

    async def create_booking(self, booking: Booking):
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking