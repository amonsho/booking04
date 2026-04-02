from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import LoginSchema, TokenSchema, GoogleRegisterSchema
from app.auth.auth import hash_password, verify_password
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.dependencies import get_current_user
from app.core.config import settings

from fastapi.security import OAuth2PasswordRequestForm

from google.oauth2 import id_token as google_id_token
from google.auth.transport.requests import Request as GoogleRequest

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User created"}

@router.post("/login", response_model=TokenSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    
    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub":str(db_user.id)})

    return {"access_token": access_token,
            "refresh_token": refresh_token, 
            "token_type": "bearer"}


# @router.post("/google/register", response_model=TokenSchema)
# async def google_register(
#     payload: GoogleRegisterSchema,
#     db: AsyncSession = Depends(get_db),
# ):
#     if not settings.GOOGLE_CLIENT_ID:
#         raise HTTPException(
#             status_code=500,
#             detail="GOOGLE_CLIENT_ID is not set in .env",
#         )

#     try:
#         # Verifies the Google-signed ID token and returns its claims.
#         info = google_id_token.verify_oauth2_token(
#             payload.id_token,
#             GoogleRequest(),
#             audience=settings.GOOGLE_CLIENT_ID,
#         )
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid Google token")

#     email = info.get("email")
#     name = info.get("name") or (email.split("@")[0] if email else None)
#     avatar = info.get("picture")

#     if not email or not name:
#         raise HTTPException(status_code=400, detail="Google token missing email/name")

#     result = await db.execute(select(User).where(User.email == email))
#     existing_user = result.scalar_one_or_none()

#     if existing_user:
#         # Refresh display fields (optional)
#         if avatar and existing_user.avatar != avatar:
#             existing_user.avatar = avatar
#         if name and existing_user.name != name:
#             existing_user.name = name
#         await db.commit()
#         await db.refresh(existing_user)
#         user_obj = existing_user
#     else:
#         # Password is required by the schema, but for Google auth we use a random one.
#         random_password = secrets.token_urlsafe(24)
#         user_obj = User(
#             name=name,
#             email=email,
#             password=hash_password(random_password),
#             avatar=avatar,
#         )
#         db.add(user_obj)
#         await db.commit()
#         await db.refresh(user_obj)

#     access_token = create_access_token({"sub": str(user_obj.id)})
#     refresh_token = create_refresh_token({"sub": str(user_obj.id)})

#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }

