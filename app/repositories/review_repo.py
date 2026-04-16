from sqlalchemy import select, func
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
                Review.hotel_id == hotel_id,
                Review.is_deleted == False
            )
        )
        return result.scalars().first()
    
    async def get_hotel_reviews(self, hotel_id:int, limit:int, offset:int):
        result = await self.session.execute(
            select(Review).where(
                Review.hotel_id == hotel_id,
                Review.is_deleted == False
            ).limit(limit).offset(offset)
        )
        return result.scalars().all()
    
    async def get_average_rating(self, hotel_id:int):
        result = await self.session.execute(
            select(func.avg(Review.rating)).where(
                Review.hotel_id == hotel_id,
                Review.is_deleted == False
            )
        )
        return result.scalar()
    
    async def get_by_id(self, review_id: int):
        result = await self.session.execute(
            select(Review).where(Review.id == review_id, Review.is_deleted == False)
        )
        return result.scalars().first()
    
    async def delete(self, review: Review):
        review.is_deleted = True
        await self.session.commit()