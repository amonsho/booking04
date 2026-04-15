import stripe
from app.core.config import settings
from app.models.payment import Payment
from app.models.enums import PaymentStatus

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    def __init__(self, repo):
        self.repo = repo

    async def create_payment(self, booking, amount):

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Booking #{booking.id}"
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            success_url=settings.FRONTEND_URL + "/success",
            cancel_url=settings.FRONTEND_URL + "/cancel",

            metadata={
                "booking_id": str(booking.id)
            }
        )

        payment = Payment(
            booking_id=booking.id,
            provider="stripe",
            status=PaymentStatus.pending,
            amount=amount,
            provider_payment_id=session.id  # Store Session ID (cs_...)
        )
        await self.repo.create(payment)

        return {
            "checkout_url": session.url
        }
    
    async def refund_payment(self, session_or_intent_id: str):
        if session_or_intent_id.startswith("cs_"):
            # It's a Checkout Session, we need the Payment Intent
            session = stripe.checkout.Session.retrieve(session_or_intent_id)
            if not session.payment_intent:
                # User never completed the payment during this session
                return None
            payment_intent_id = session.payment_intent
        else:
            payment_intent_id = session_or_intent_id

        refund = stripe.Refund.create(
            payment_intent=payment_intent_id
        )
        return refund