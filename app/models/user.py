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

    avatar = Column(String, nullable=True)

    bookings = relationship("Booking", back_populates="user")
