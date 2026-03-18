from fastapi import APIRouter, Depends, HTTPException ,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.booking import BookingCreate, BookingResponse
from app.db.session import get_db
from app.models import booking
from app.auth.dependencies import get_current_user


class BookingService : 
    def __init__(self,db:AsyncSession):
        self.db = db
        
    async def create_booking(booking:BookingCreate,db:AsyncSession = Depends(get_db)):
        if booking.date_to <= booking.date_from : 
            raise HTTPException (status_code=400, detail="date_to must be greater than date_from")
        
        new_booking = booking(
        **booking.model_dump(),
        status="pending",
        total_price=None,
        user_id=get_current_user["id"]
    )

        db.add(new_booking)
        await db.commit()
        await db.refresh(new_booking)

        return BookingResponse.model_validate(new_booking)