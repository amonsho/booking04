from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES:int

    DATABASE_URL: str

    # Google Identity Services client id (Frontend uses this value; no secret here)
    GOOGLE_CLIENT_ID: Optional[str] = None

    class Config:
        env_file = ".env"

settings = Settings()