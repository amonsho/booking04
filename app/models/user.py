from sqlalchemy import Column, String,Enum,Boolean
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
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)

    bookings = relationship("Booking", back_populates="user")
    reviews = relationship("Review", back_populates="user")
