from sqlalchemy import Column, Integer, String,ForeignKey,Float,Date
from sqlalchemy.orm import relationship 
from app.models.conf import BaseModelClass

class Room(BaseModelClass):
    __tablename__ = "rooms"

    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    room_type = Column(String)
    price = Column(Float)

    hotel = relationship("Hotel", back_populates="rooms")