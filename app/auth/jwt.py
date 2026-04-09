from datetime import datetime, timedelta, timezone
from jose import jwt

from app.core.config import settings

def create_access_token(data:dict):
    to_encode = data.copy()

    expire_timestamp = int((datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
    to_encode.update({"exp": expire_timestamp})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def create_refresh_token(data:dict):
    to_encode = data.copy()

    expire_timestamp = int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp())
    to_encode.update({"exp": expire_timestamp})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )