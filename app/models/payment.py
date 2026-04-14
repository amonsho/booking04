from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from app.models.enums import PaymentStatus
from app.db.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"))

    provider = Column(String)

    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.pending,
        nullable=False
    )

    amount = Column(Float)

    provider_payment_id = Column(String)