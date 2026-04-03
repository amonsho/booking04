from sqlalchemy import Column, String,Enum
from sqlalchemy.orm import relationship
from app.models.conf import BaseModelClass
from app.models.enums import UserRole

class User(BaseModelClass):
    __tablename__ = "users"

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    google_id = Column(String, unique=True, nullable=True)

    avatar = Column(String, nullable=True)

    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")
