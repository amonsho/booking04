from sqlalchemy import Column, Integer, ForeignKey, Date, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.conf import BaseModelClass

class Booking(BaseModelClass):
    __tablename__ = "bookings"

    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))

    date_from = Column(Date)
    date_to = Column(Date)

    status = Column(String, default="pending")
    total_price = Column(Integer)
    guests = Column(Integer, default=1)

    created_at = Column(Date, server_default=func.now())

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")