from sqlalchemy import select
from app.models.booking import Booking
from app.models.room import Room 

class BookingRepository:
    def __init__(self, db):
        self.db = db

    async def get_room_by_id(self, room_id: int):
        result = await self.db.execute(
            select(Room).where(Room.id == room_id, Room.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def create_booking(self, booking: Booking):
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def check_overlap(self, room_id: int, date_from, date_to):
        from sqlalchemy import and_, or_
        # Ensure we only check against confirmed bookings (or pending ones if you don't want anyone to hold the room)
        # Assuming we check all bookings that overlap
        result = await self.db.execute(
            select(Booking).where(
                Booking.room_id == room_id,
                Booking.is_deleted == False,
                or_(
                    and_(Booking.date_from <= date_from, Booking.date_to >= date_from),
                    and_(Booking.date_from <= date_to, Booking.date_to >= date_to),
                    and_(Booking.date_from >= date_from, Booking.date_to <= date_to)
                )
            )
        )
        return result.scalars().first() is not None

    async def get_bookings_by_user(self, user_id: int):
        result = await self.db.execute(
            select(Booking).where(Booking.user_id == user_id, Booking.is_deleted == False)
        )
        return result.scalars().all()
    


    async def get_bookings_by_room(self, room_id: int):
        result = await self.db.execute(
        select(Booking).where(Booking.room_id == room_id, Booking.is_deleted == False)
        )
        return result.scalars().all()

    async def get_by_id(self, booking_id: int):
        result = await self.db.execute(
            select(Booking).where(Booking.id == booking_id, Booking.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def _get_by_id_any(self, booking_id: int):
        result = await self.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def get_deleted_all(self):
        result = await self.db.execute(
            select(Booking).where(Booking.is_deleted == True)
        )
        return result.scalars().all()

    async def restore(self, booking_id: int):
        booking = await self._get_by_id_any(booking_id)
        if not booking:
            return None
        
        booking.is_deleted = False
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def delete_booking_by_id(self, booking_id: int):
        booking = await self.get_by_id(booking_id)
        if not booking:
            return False
        booking.is_deleted = True
        await self.db.commit()
        return True