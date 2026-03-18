from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import BookingService
from app.auth.dependencies import get_current_user  

booking_router = APIRouter(prefix="/booking", tags=["Booking"])


@booking_router.post("/", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    service = BookingService(db)

    return await service.create_booking(
        booking,
        current_user.id
    )