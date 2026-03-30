from sqlalchemy import Column, Integer, ForeignKey, Date, String, Boolean, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.models.conf import BaseModelClass
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Booking(BaseModelClass):
    __tablename__ = "bookings"

    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))

    date_from = Column(Date)
    date_to = Column(Date)

    total_price = Column(Integer)
    guests = Column(Integer, default=1)

    # created_at should use a callable default (no parentheses)
    created_at = Column(Date, default=datetime.utcnow)
    is_available = Column(Boolean, default=False)

    # single status column using SQLAlchemy Enum for strong typing
    status = Column(SqlEnum(BookingStatus), default=BookingStatus.PENDING)

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
