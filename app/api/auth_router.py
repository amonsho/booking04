from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.auth import LoginSchema, TokenSchema
from app.auth.auth import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user

from fastapi.security import OAuth2PasswordRequestForm

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
    # Ищем пользователя по email (username в форме)
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid credentials"
        )

    # Создаём JWT токен
    token = create_access_token({"sub": str(db_user.id)})

    return {"access_token": token, "token_type": "bearer"}

# @router.post("/login", response_model=Token)
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
#     db_user = db.query(User).filter(User.email == form_data.username).first()

#     if not db_user or not verify_password(form_data.password, db_user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     access_token = create_access_token({"sub":db_user.email})

#     return {
#         "access_token": access_token,
#         "token_type": "bearer"
#     }

@router.get("/me")
async def get_me(user_id: int = Depends(get_current_user)):
    return {"user_id": user_id}