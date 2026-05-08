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

router = APIRouter(prefix="/payment", tags=["Payment"], redirect_slashes=False)

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

@router.post("/payments/webhook/")
@router.post("/payments/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    print(f"--- Webhook received! Method: {request.method} ---")
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    print(f"Signature: {sig_header}")

@router.get("/payments/webhook")
async def debug_webhook_get(request: Request):
    print("!!! WARNING: Received GET request on webhook endpoint !!!")
    print(f"Headers: {request.headers}")
    return {"message": "Webhooks must be POST, but you sent a GET. Check for redirects (http->https or trailing slashes)."}

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
    
    if event.type == "checkout.session.completed":

        session = event.data.object

        metadata = getattr(session, "metadata", {}) or {}
        
        try:
            booking_id = metadata["booking_id"] if "booking_id" in metadata else None
        except TypeError:
            booking_id = getattr(metadata, "booking_id", None)

        if not booking_id:
            raise HTTPException(status_code=404, detail="Booking not found in metadata")

        repo = BookingRepository(db)
        booking = await repo.get_by_id(int(booking_id))

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found in db")
        
        # We must use proper Enum values (lowercase values defined in Enums)
        from app.models.booking import BookingStatus
        if hasattr(booking, 'status') and booking.status == BookingStatus.CONFIRMED:
            return {"status":"already processed"}
        
        booking.status = BookingStatus.CONFIRMED
        db.add(booking)

        # Also update payment status
        from sqlalchemy import select
        from app.models.payment import Payment
        from app.models.enums import PaymentStatus
        
        payment_query = await db.execute(select(Payment).where(Payment.provider_payment_id == session.id))
        payment = payment_query.scalar_one_or_none()
        
        if payment:
            payment.status = PaymentStatus.completed
            # Swap the Session ID (cs_...) with the actual Payment Intent ID (pi_...) for refunds
            if hasattr(session, "payment_intent") and session.payment_intent:
                payment.provider_payment_id = session.payment_intent
            db.add(payment)

        await db.commit()
        await db.refresh(booking)

    return {"status":"ok"}

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