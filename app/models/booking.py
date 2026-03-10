from sqlalchemy import Column, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from models.conf import BaseModelClass

class Booking(BaseModelClass):
    __tablename__ = "bookings"

    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))

    date_from = Column(Date)
    date_to = Column(Date)

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")