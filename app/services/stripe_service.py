import stripe
from app.core.config import settings

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

        return {
            "checkout_url": session.url
        }