from fastapi import HTTPException

from app.models.review import Review
from app.repositories.review_repo import ReviewRepository

class ReviewService:
    def __init__(self, repo:ReviewRepository):
        self.repo = repo

    async def create_review(
            self,
            user_id:int,
            hotel_id:int,
            rating:int,
            comment:str
    ):
        #proverka reytinga
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Рейтинг должен быть от 1 до 5")
        
        #exist or no 
        existing_review = await self.repo.get_user_review_for_hotel(user_id, hotel_id)

        if existing_review:
            raise HTTPException(status_code=400, detail="Вы уже оставили отзыв об этом отеле.")
        
        review = Review(
            user_id=user_id,
            hotel_id=hotel_id,
            rating=rating,
            comment=comment
        )

        return await self.repo.create(review)