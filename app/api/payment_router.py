from datetime import datetime
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
from app.models.payment import Payment
from app.services.stripe_service import StripeService

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
    
    from app.models.booking import BookingStatus
    if hasattr(booking, 'status') and booking.status == BookingStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Booking is already paid and confirmed")
    

    manager = PaymentManager(repo)
    service = manager.get_service(data.provider)

    result = await service.create_payment(booking, data.amount)

    return result

@router.post("/payments/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    # Логгируем в файл для надежности
    with open("webhook.log", "a") as f:
        f.write(f"\n--- {datetime.now()} Webhook received ---\n")
        
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            f.write(f"Event type: {event.type}\n")
        except Exception as e:
            f.write(f"Error constructing event: {str(e)}\n")
            raise HTTPException(status_code=400, detail=str(e))
        
        if event.type == "checkout.session.completed":
            session = event.data.object
            metadata = session.get("metadata", {})
            booking_id = metadata.get("booking_id")
            
            f.write(f"Session ID: {session.id}\n")
            f.write(f"Booking ID from metadata: {booking_id}\n")

            if not booking_id:
                f.write("Error: No booking_id in metadata\n")
                return {"status": "no booking_id"}

            repo = BookingRepository(db)
            booking = await repo.get_by_id(int(booking_id))

            if not booking:
                f.write(f"Error: Booking {booking_id} not found in DB\n")
                return {"status": "booking not found"}
            
            f.write(f"Current status: {booking.status}\n")
            
            from app.models.booking import BookingStatus
            if booking.status == BookingStatus.CONFIRMED:
                f.write("Already confirmed.\n")
                return {"status": "already processed"}
            
            booking.status = BookingStatus.CONFIRMED
            db.add(booking)
            f.write("Updating status to confirmed...\n")

            # Update payment
            from sqlalchemy import select
            from app.models.payment import Payment
            from app.models.enums import PaymentStatus
            
            payment_query = await db.execute(select(Payment).where(Payment.provider_payment_id == session.id))
            payment = payment_query.scalar_one_or_none()
            
            if payment:
                payment.status = PaymentStatus.completed
                if session.get("payment_intent"):
                    payment.provider_payment_id = session.payment_intent
                db.add(payment)
                f.write("Payment record updated.\n")

            await db.commit()
            f.write("🎉 Database COMMIT successful!\n")
            
    return {"status": "ok"}

@router.post("/payments/{payment_id}/refund")
async def refund_payment(payment_id: int, db:AsyncSession = Depends(get_db)):
    payment = await db.get(Payment, payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail="payment not found")
    
    if not payment.provider_payment_id or not payment.provider_payment_id.startswith("pi_"):
        raise HTTPException(status_code=400, detail="Cannot refund a pending or invalid payment. Refund only works for completed payments.")

    repo = PaymentRepository(db)
    service = StripeService(repo)

    try:
        refund = await service.refund_payment(payment.provider_payment_id)
        payment.status = "refunded"
        await db.commit()
        return {"status": "refunded", "refund_id": refund.id}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")