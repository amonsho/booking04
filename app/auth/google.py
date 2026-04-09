from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.base_client.errors import MismatchingStateError

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.config import settings

from app.repositories.user_repo import UserRepository
from app.services.google_service import GoogleService
from app.auth.dependencies import get_current_user, get_user_by_token


router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile", "prompt":"select_account"},
)

class GoogleToken(BaseModel):
    id_token: str

@router.post("/register")
async def google_register_post(data: GoogleToken, db: AsyncSession = Depends(get_db)):
    try:
        user_info = id_token.verify_oauth2_token(
            data.id_token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

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
            "is_verified": result["user"].is_verified
        },
    }


@router.get("/register")
async def google_register(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):

    # защита от второго запроса
    if not request.session:
        return {"detail": "Duplicate callback ignored"}

    try:
        token = await oauth.google.authorize_access_token(request)
    except MismatchingStateError:
        return {"detail": "Invalid session"}
    except Exception:
        raise HTTPException(status_code=401, detail="Token error")

    # user info
    try:
        user_info = await oauth.google.parse_id_token(request, token)
    except Exception:
        resp = await oauth.google.get(
            "https://openidconnect.googleapis.com/v1/userinfo", token=token
        )
        user_info = resp.json()

    # service layer
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

@router.get('/link')
async def google_link(request: Request, token: str, db: AsyncSession = Depends(get_db)):
    # Authenticate manually via token in query param
    current_user = await get_user_by_token(token, db)
    # Store user id in session for the callback
    request.session["link_user_id"] = current_user.id
    
    redirect_uri = "http://localhost:8000/auth/google/link/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

from app.auth.dependencies import get_current_user

@router.get("/link/callback")
async def google_link_callback(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Retrieve user_id from session
    user_id = request.session.get("link_user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User session not found")
    
    # Clean up session
    request.session.pop("link_user_id", None)
    
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        raise HTTPException(status_code=400, detail="Google auth error")
    
    # user info
    user_info = None
    if "id_token" in token:
        try:
            user_info = await oauth.google.parse_id_token(request, token)
        except Exception:
            user_info = None
            
    if not user_info:
        resp = await oauth.google.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            token=token
        )
        user_info = resp.json()

    google_id = user_info.get("sub")
    if not google_id:
        raise HTTPException(status_code=400, detail="No google_id")

    repo = UserRepository(db)
    # Fetch the user using the ID from session
    current_user = await repo.get_by_id(user_id)
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    service = GoogleService(repo)
    try:
        await service.link_google(current_user, google_id)
        print(f"[DEBUG] User {current_user.email} linked to Google ID {google_id}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Redirect back to the frontend profile page
    frontend_profile_url = f"{settings.FRONTEND_URL}/profile"
    return RedirectResponse(url=frontend_profile_url)
