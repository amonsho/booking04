from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES:int

    DATABASE_URL: str

    SESSION_SECRET_KEY: str

    # Google Identity Services client id (Frontend uses this value; no secret here)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    # Frontend URL to redirect to after successful OAuth (include protocol)
    FRONTEND_URL: Optional[str] = None

    BREVO_API_KEY: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLIC_KEY: Optional[str] = None

    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()