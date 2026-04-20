from fastapi import APIRouter, Depends, HTTPException,Query, BackgroundTasks
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

from app.services.email_service import EmailService
from itsdangerous import URLSafeTimedSerializer
email_service = EmailService()

# Функции для генерации токена
def generate_email_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt="email-confirm")

def send_verification_email_background(email: str, token: str):
    link = f"{settings.FRONTEND_URL}/verify?token={token}"
    subject = "Verify your BookingPro account"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify your Email</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f7f9; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); }}
            .header {{ background-color: #1E3A8A; padding: 40px 20px; text-align: center; }}
            .header h1 {{ color: #ffffff; margin: 0; font-size: 28px; letter-spacing: 1px; font-weight: 700; }}
            .content {{ padding: 40px 30px; line-height: 1.6; color: #333333; }}
            .content h2 {{ font-size: 22px; color: #1E3A8A; margin-top: 0; }}
            .content p {{ font-size: 16px; margin-bottom: 25px; }}
            .button-container {{ text-align: center; margin: 35px 0; }}
            .button {{ background-color: #D4AF37; color: #ffffff !important; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block; transition: background-color 0.3s ease; box-shadow: 0 4px 10px rgba(212, 175, 55, 0.3); }}
            .footer {{ background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #edf2f7; }}
            .footer p {{ font-size: 13px; color: #718096; margin: 0 0 10px 0; }}
            .link-fallback {{ font-size: 12px; color: #a0aec0; word-break: break-all; margin-top: 20px; }}
            .brand-accent {{ color: #D4AF37; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Booking<span class="brand-accent">Pro</span></h1>
            </div>
            <div class="content">
                <h2>Welcome to the family!</h2>
                <p>We're thrilled to have you join us. To start exploring premium stays and manage your bookings, please verify your email address by clicking the button below.</p>
                <div class="button-container">
                    <a href="{link}" class="button">Confirm My Account</a>
                </div>
                <p>If you didn't create an account with BookingPro, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2026 BookingPro. All rights reserved.</p>
                <p>Your comfort, our priority.</p>
                <div class="link-fallback">
                    If the button doesn't work, copy this link: {link}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    email_service.send_email(email, subject, html_content)

@router.post("/register")
async def register(user: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # Проверяем, есть ли уже такой email
    result = await db.execute(select(User).where(User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        is_verified=False
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Генерируем токен и отправляем письмо через background task
    token = generate_email_token(new_user.email)
    background_tasks.add_task(send_verification_email_background, new_user.email, token)

    return {"message": "User created, please check your email to verify your account"}

@router.get("/test-email")
def test_email():
    email_service.send_email(
        "amonsho004@gmail.com",
        "Test Email",
        "<h3>Hello!</h3><p>This is a test email from FastAPI + Brevo</p>"
    )
    return {"message": "Email sent, check your inbox"}

# @router.post("/register")
# async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):

#     result = await db.execute(select(User).where(User.email == user.email))
#     existing_user = result.scalar_one_or_none()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     new_user = User(
#         name=user.name,
#         email=user.email,
#         password=hash_password(user.password)
#     )

#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)

#     return {"message": "User created"}

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

@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    refresh_token = payload.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token required")
    
    try:
        from jose import jwt, JWTError
        payload = jwt.decode(
            refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={"leeway": 60}
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        access_token = create_access_token({"sub": str(user_id)})
        new_refresh_token = create_refresh_token({"sub": str(user_id)})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


from app.services.user_service import UserService
from app.repositories.user_repo import UserRepository

@router.get("/verify")
async def verify_email(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    email = UserService.confirm_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    repo = UserRepository(db)
    user = await repo.get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "Email already verified"}

    user.is_verified = True
    await db.commit()
    return {"message": "Email verified successfully"}




