from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from sqlalchemy import select
from app.models.user import User
import secrets

from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.auth import hash_password
from authlib.integrations.base_client.errors import MismatchingStateError

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

oauth = OAuth()

oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/register")
async def google_register(request: Request):
    redirect_uri = getattr(
        settings, "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
    )
    resp = await oauth.google.authorize_redirect(request, redirect_uri)
    try:
        print("[google_register] redirect to:", resp.headers.get("location"))
    except Exception:
        pass
    return resp


@router.get("/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except MismatchingStateError:
        raise HTTPException(
            status_code=400,
            detail=(
                "CSRF detected: state mismatch. Start the login flow from /auth/google/register "
                "and ensure cookies are enabled in the browser."
            ),
        )
    except Exception:
        raise HTTPException(
            status_code=401, detail="Failed to obtain token from Google"
        )

    if not token:
        raise HTTPException(
            status_code=401, detail="Failed to obtain token from Google"
        )

   
    user_info = None
    if "id_token" in token:
        try:
            user_info = await oauth.google.parse_id_token(request, token)
        except Exception:
            user_info = None

    if not user_info:
        # use full OpenID Connect userinfo endpoint to avoid relative URL issues
        resp = await oauth.google.get(
            "https://openidconnect.googleapis.com/v1/userinfo", token=token
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=401, detail="Failed to fetch userinfo from Google"
            )
        user_info = resp.json()

    email = user_info.get("email")
    name = user_info.get("name") or (email.split("@")[0] if email else None)
    avatar = user_info.get("picture")

    if not email or not name:
        raise HTTPException(
            status_code=400, detail="Google response missing email/name"
        )

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if avatar and existing_user.avatar != avatar:
            existing_user.avatar = avatar
        if name and existing_user.name != name:
            existing_user.name = name
        await db.commit()
        await db.refresh(existing_user)
        user_obj = existing_user
    else:
        random_password = secrets.token_urlsafe(24)
        user_obj = User(
            name=name,
            email=email,
            password=hash_password(random_password),
            avatar=avatar,
        )
        db.add(user_obj)
        await db.commit()
        await db.refresh(user_obj)

    access_token = create_access_token({"sub": str(user_obj.id)})
    refresh_token = create_refresh_token({"sub": str(user_obj.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_obj.id,
            "email": user_obj.email,
            "name": user_obj.name,
            "avatar": user_obj.avatar,
        },
    }


# from fastapi import APIRouter, Request, Depends, HTTPException
# from authlib.integrations.starlette_client import OAuth
# from app.core.config import settings
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.db.session import get_db
# from sqlalchemy import select
# from app.models.user import User
# import secrets

# from app.auth.jwt import create_access_token, create_refresh_token
# from app.auth.auth import hash_password

# router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

# oauth = OAuth()

# oauth.register(
#     name="google",
#     client_id=settings.GOOGLE_CLIENT_ID,
#     client_secret=settings.GOOGLE_CLIENT_SECRET,
#     access_token_url="https://oauth2.googleapis.com/token",
#     authorize_url="https://accounts.google.com/o/oauth2/auth",
#     api_base_url="https://www.googleapis.com/oauth2/v1/",
#     client_kwargs={"scope": "openid email profile"},
# )


# @router.get("/login")
# async def google_login(request: Request):
#     redirect_uri = getattr(
#         settings, "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
#     )
#     return await oauth.google.authorize_redirect(request, redirect_uri)


# @router.get("/callback")
# async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
#     token = await oauth.google.authorize_access_token(request)
#     user_info = await oauth.google.parse_id_token(request, token)

#     if not user_info:
#         raise HTTPException(
#             status_code=401, detail="Failed to obtain user info from Google"
#         )

#     email = user_info.get("email")
#     name = user_info.get("name") or (email.split("@")[0] if email else None)
#     avatar = user_info.get("picture")

#     if not email or not name:
#         raise HTTPException(status_code=400, detail="Google token missing email/name")

#     result = await db.execute(select(User).where(User.email == email))
#     existing_user = result.scalar_one_or_none()

#     if existing_user:
#         if avatar and existing_user.avatar != avatar:
#             existing_user.avatar = avatar
#         if name and existing_user.name != name:
#             existing_user.name = name
#         await db.commit()
#         await db.refresh(existing_user)
#         user_obj = existing_user
#     else:
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
#         "user": {
#             "id": user_obj.id,
#             "email": user_obj.email,
#             "name": user_obj.name,
#             "avatar": user_obj.avatar,
#         },
#     }
