from app.repositories.user_repo import UserRepository
from app.models.user import User
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.auth import hash_password

import secrets


class GoogleService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def login_or_register(self, user_info: dict):
        google_id = user_info.get("sub")
        email = user_info.get("email")
        name = user_info.get("name") or (email.split("@")[0] if email else None)
        avatar = user_info.get("picture")

        if not google_id:
            raise Exception("No google_id")

        user = await self.repo.get_by_google_id(google_id)

        if not user:
            user = await self.repo.get_by_email(email)

        # if not email or not name:
        #     raise Exception("Invalid Google data")

        # user = await self.repo.get_by_email(email)

        if user:
            # обновляем
            # если есть user но нет google_id  привязываем
            if not user.google_id:
                user.google_id = google_id

            if avatar and user.avatar != avatar:
                user.avatar = avatar
            if name and user.name != name:
                user.name = name

            user = await self.repo.update(user)

        else:
            # создаём
            random_password = secrets.token_urlsafe(24)

            user = User(
                name=name,
                email=email,
                password=hash_password(random_password),
                avatar=avatar,
                google_id=google_id
            )

            user = await self.repo.create(user)

        # создаём токены
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user,
        }
    
    async def link_google(self, user, google_id:str):
        existing = await self.repo.get_by_google_id(google_id)

        if existing:
            raise Exception("Google already used")
        
        if user.google_id:
            raise Exception("Already linked")
        
        user.google_id = google_id
        user = await self.repo.update(user)

        return user
