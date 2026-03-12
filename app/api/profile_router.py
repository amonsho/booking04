from fastapi import Depends, APIRouter, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import shutil
import os

from app.db.session import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

@router.get("/")
async def get_profile(
    user_id: int = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none

    return user

@router.post("/avatar")
async def upload_avatar(
        file: UploadFile = File(...),
        user_id: int = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    filname = f"user_{user_id}_{file.filename}"
    filepath = os.path.join("media/avatars", filname)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    user.avatar = filepath

    await db.commit()
    await db.refresh(user)

    return {"avatar": filepath}