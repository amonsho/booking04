from fastapi import APIRouter, Depends
from app.models.user import User
from app.auth.dependencies import get_current_user

from app.schemas.user import ChangePasswordSchema, UserRead
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)):
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