from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.review import ReviewCreate, ReviewResponse
from app.repositories.review_repo import ReviewRepository
from app.services.review_service import ReviewService
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewResponse)
async def create_review(
    data:ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = ReviewRepository(db)
    service = ReviewService(repo)

    review = await service.create_review(
        user_id=current_user.id,
        hotel_id=data.hotel_id,
        rating=data.rating,
        comment=data.comment
    )
    return review