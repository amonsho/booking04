from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import BookingService
from app.auth.dependencies import get_current_user, get_admin_user
from app.models.booking import Booking

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


@booking_router.get("/me", response_model=list[BookingResponse])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    service = BookingService(db)
    return await service.get_user_bookings(current_user.id)


@booking_router.get("/all", response_model=list[BookingResponse])
async def get_all_bookings(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user),
):
    """Get all bookings — admin only."""
    result = await db.execute(select(Booking).limit(limit).offset(offset))
    return result.scalars().all()


@booking_router.delete("/{booking_id}")
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can delete booking"
        )

    service = BookingService(db)
    return await service.delete_booking(booking_id)