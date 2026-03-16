from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.services.admin_service import AdminSerivce
from app.auth.dependencies import get_admin_user
from app.models.enums import UserRole

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user)
):
    repo = UserRepository(db)
    service = AdminSerivce(repo)

    return await service.get_all_users()

@router.delete("/users/{user_id}")
async def delete_user(
    user_id:int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user)
):
    repo = UserRepository(db)
    service = AdminSerivce(repo)

    return await service.delete_user(user_id)

@router.patch("/users/{user_id}/role")
async def change_user_role(
    user_id: int,
    role: UserRole,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user)
):
    repo = UserRepository(db)
    service = AdminSerivce(repo)

    return await service.change_user_role(user_id, role)

