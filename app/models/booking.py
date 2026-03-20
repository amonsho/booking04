from sqlalchemy import Column, Integer, ForeignKey, Date, String ,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.conf import BaseModelClass
from datetime import datetime

class Booking(BaseModelClass):
    __tablename__ = "bookings"

    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))

    date_from = Column(Date)
    date_to = Column(Date)

    status = Column(String, default="pending")
    total_price = Column(Integer)
    guests = Column(Integer, default=1)

    created_at = Column(Date, default=datetime.utcnow())
    is_available = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")