from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.conf import BaseModelClass

class User(BaseModelClass):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    bookings = relationship("Booking", back_populates="user")
