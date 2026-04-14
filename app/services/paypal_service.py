import httpx
from app.services.payment_service import PaymentService
from app.models.payment import Payment

class PayPalService(PaymentService):
    def __init__(self, repo):
        self.repo = repo

    async def create_payment(self, booking, amount):

        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api-m.sandbox.paypal.com/v2/checkout/orders",
                json={
                    "intent": "CAPTURE",
                    "purchase_units": [
                        {
                            "amount": {
                                "currency_code": "USD",
                                "value": str(amount)
                            }
                        }
                    ]
                },
                headers={
                    "Authorization": "Bearer YOUR_ACCESS_TOKEN"
                }
            )

        data = response.json()

        
        payment = Payment(
            booking_id=booking.id,
            provider="paypal",
            provider_payment_id=data["id"],
            status="pending",
            amount=amount
        )

        await self.repo.create(payment)

        return data["links"] 