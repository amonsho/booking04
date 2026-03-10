from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.conf import BaseModelClass

class Room(BaseModelClass):
    __tablename__ = "rooms"

    title = Column(String, nullable=False)
    price = Column(Integer)

    bookings = relationship("Booking", back_populates="room")