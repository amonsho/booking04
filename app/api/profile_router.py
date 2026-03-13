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

    user = await repo.get_by_id(user_id)

    return user

@router.post("/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        user_id: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)

    user = await repo.get_by_id(user_id)

    filname = f"user_{user_id}_{file.filename}"
    filepath = os.path.join("media/avatars", filname)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    user.avatar = filepath

    await repo.update(user)

    return {"avatar": filepath}

@router.patch("/")
async def update_profile(
    data:ProfileUpdate,
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)

    if data.name:
        user.name = data.name

    await repo.update(user)

    return user