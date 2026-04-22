from sqlalchemy import Column, Integer, String,ForeignKey,Float,Boolean
from sqlalchemy.orm import relationship 
from app.models.conf import BaseModelClass

class Room(BaseModelClass):
    __tablename__ = "rooms"

    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    room_type = Column(String)
    number_room = Column(Integer)
    price = Column(Float)
    wifi = Column(Boolean)
    photos = Column(String)
    is_available = Column(Boolean, default=True)
    
    
    
    bookings = relationship("Booking", back_populates="room")
    hotel = relationship("Hotel", back_populates="rooms")