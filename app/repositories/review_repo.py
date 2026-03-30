from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review

class ReviewRepository:
    def __init__(self, session:AsyncSession):
        self.session = session

    async def create(self, review:Review):
        self.session.add(review)
        await self.session.commit()
        await self.session.refresh(review)
        return review
    
    async def get_user_review_for_hotel(self, user_id:int, hotel_id:int):
        result = await self.session.execute(
            select(Review).where(
                Review.user_id == user_id,
                Review.hotel_id == hotel_id
            )
        )
        return result.scalars().first()
    
    async def get_hotel_reviews(self, hotel_id:int):
        result = await self.session.execute(
            select(Review).where(Review.hotel_id == hotel_id)
        )
        return result.scalars().all()