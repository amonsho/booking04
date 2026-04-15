from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.schemas.booking import BookingCreate, BookingResponse
from app.services.booking_service import BookingService
from app.auth.dependencies import get_current_user, get_admin_user
from app.models.booking import Booking

from app.repositories.booking_repository import BookingRepository
from app.models.booking import BookingStatus
from app.models.enums import PaymentStatus
from app.services.stripe_service import StripeService
from app.models.payment import Payment

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

@booking_router.post("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    # 1. найти booking
    repo = BookingRepository(db)
    booking = await repo.get_by_id(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # 2. если уже отменён
    if booking.status == BookingStatus.CANCELLED:
        return {"status": "already cancelled"}

    # 3. найти payment
    result = await db.execute(
        select(Payment).where(Payment.booking_id == booking.id).order_by(Payment.id.desc())
    )
    payment = result.scalars().first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # 4. защита от двойного refund
    if payment.status == PaymentStatus.refunded:
        return {"status": "already refunded"}

    # 5. проверка payment_intent (у тебя это provider_payment_id)
    if not payment.provider_payment_id:
        raise HTTPException(
            status_code=400,
            detail="No payment_intent_id found"
        )

    # 6. Stripe refund
    from app.repositories.payment_repo import PaymentRepository
    payment_repo = PaymentRepository(db)
    stripe_service = StripeService(payment_repo)

    refund = await stripe_service.refund_payment(
        payment.provider_payment_id  # ← ВАЖНО
    )

    # 7. обновляем booking
    booking.status = BookingStatus.CANCELLED

    # 8. обновляем payment
    payment.status = PaymentStatus.refunded

    db.add(booking)
    db.add(payment)

    await db.commit()

    return {
        "status": "cancelled",
        "refund": "success",
        "refund_id": refund.id
    }