from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.conf import BaseModelClass

class Review(BaseModelClass):
    __tablename__ = "reviews"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id"), nullable=False)

    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)

    user = relationship("User", back_populates="reviews")
    hotel = relationship("Hotel", back_populates="reviews")