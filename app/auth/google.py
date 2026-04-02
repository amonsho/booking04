from fastapi import APIRouter, Request, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import MismatchingStateError

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.config import settings

from app.repositories.user_repo import UserRepository
from app.services.google_service import GoogleService


router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile", "prompt":"select_account"},
)


@router.get("/register")
async def google_register(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):

    # 🔥 защита от второго запроса
    if not request.session:
        return {"detail": "Duplicate callback ignored"}

    try:
        token = await oauth.google.authorize_access_token(request)
    except MismatchingStateError:
        return {"detail": "Invalid session"}
    except Exception:
        raise HTTPException(status_code=401, detail="Token error")

    # 🔹 user info
    try:
        user_info = await oauth.google.parse_id_token(request, token)
    except Exception:
        resp = await oauth.google.get(
            "https://openidconnect.googleapis.com/v1/userinfo", token=token
        )
        user_info = resp.json()

    # 🔹 service layer
    repo = UserRepository(db)
    service = GoogleService(repo)

    result = await service.login_or_register(user_info)

    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "token_type": "bearer",
        "user": {
            "id": result["user"].id,
            "email": result["user"].email,
            "name": result["user"].name,
            "avatar": result["user"].avatar,
        },
    }