from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user

from app.schemas.user import ChangePasswordSchema
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me")
async def get_me(user_id: int = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    return user

@router.post("/change-password")
async def change_password(
    data: ChangePasswordSchema,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    service = UserService(repo)

    return await service.change_password(current_user.id, data)