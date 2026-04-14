class PaymentService:
    async def create_payment(self, booking, amount):
        raise NotImplementedError

    async def capture_payment(self, booking, amount):
        raise NotImplementedError   
