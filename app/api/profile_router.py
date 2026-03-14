from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import shutil
import os

from app.db.session import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user

from app.schemas.profile import ProfileUpdate
from app.repositories.user_repo import UserRepository
from app.services.user_service import UserService

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

@router.get("/")
async def get_profile(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)

    service = UserService(repo)

    return await service.get_profile(user_id)

@router.post("/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        user_id: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)

    service = UserService(repo)

    avatar = await service.upload_avatar(user_id, file)

    return {"avatar": avatar}

@router.patch("/")
async def update_profile(
    data:ProfileUpdate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    
    service = UserService(repo)

    return await service.update_profile(user_id, data)