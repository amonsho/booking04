from fastapi import APIRouter, Depends,HTTPException,Request
from app.repositories.payment_repo import PaymentRepository
from app.repositories.booking_repository import BookingRepository
from app.services.payment_manager import PaymentManager
from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.schemas.payment import CreatePaymentSchema
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import BookingStatus

from app.repositories.booking_repository import BookingRepository

import stripe
from app.core.config import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/payments/create")
async def create_payment(data:CreatePaymentSchema, session=Depends(get_db), current_user=Depends(get_current_user)):
    repo = PaymentRepository(session)
    booking_repo = BookingRepository(session)

    booking = await booking_repo.get_by_id(data.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your booking")
    

    manager = PaymentManager(repo)
    service = manager.get_service(data.provider)

    result = await service.create_payment(booking, data.amount)

    return result

@router.post("/payments/webhook")
async def stripe_webhook(request:Request, db: AsyncSession = Depends(get_db)):

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print(f"Webhook error: invalid payload. Payload: {payload}, Error: {e}")
        raise HTTPException(status_code=400, detail="invalid payload")
    
    except stripe.error.SignatureVerificationError as e:
        print(f"Webhook error: invalid signature. Secret used: {endpoint_secret}, Error: {e}")
        raise HTTPException(status_code=400, detail="invalid signature")
    except Exception as e:
        print(f"Webhook error: unknown exception. Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        booking_id = session["metadata"].get("booking_id")

        repo = BookingRepository(db)
        booking = await repo.get_by_id(int(booking_id))

        if not booking_id:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        booking.status = BookingStatus.CONFIRMED

        await db.commit()


        print(f'Booking {booking_id} PAID success')
    
    return {"status":"ok"}