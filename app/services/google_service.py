from app.repositories.user_repo import UserRepository
from app.models.user import User
from app.auth.jwt import create_access_token, create_refresh_token
from app.auth.auth import hash_password

import secrets


class GoogleService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def login_or_register(self, user_info: dict):
        email = user_info.get("email")
        name = user_info.get("name") or (email.split("@")[0] if email else None)
        avatar = user_info.get("picture")

        if not email or not name:
            raise Exception("Invalid Google data")

        user = await self.repo.get_by_email(email)

        if user:
            # обновляем
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