from app.services.paypal_service import PayPalService
from app.services.stripe_service import StripeService

class PaymentManager:
    def __init__(self, repo):
        self.repo = repo

    def get_service(self, provider: str):
        if provider == "paypal":
            return PayPalService(self.repo)

        if provider == "stripe":
            return StripeService(self.repo)