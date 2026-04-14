from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, session):
        self.session = session

    async def create(self, payment):
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
    
    async def get_by_id(self, payment_id):
        return await self.session.get(Payment, payment_id)