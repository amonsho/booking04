from app.repositories.user_repo import UserRepository
import os
import shutil

class UserService:
    def __init__(self, repo:UserRepository):
        self.repo = repo

    async def get_profile(self, user_id:int):
        user = await self.repo.get_by_id(user_id)
        return user
    
    async def update_profile(self, user_id:int, data):
        user = await self.repo.get_by_id(user_id)

        if data.name:
            user.name = data.name

        # if data.email:
        #     user.email = data.email

        await self.repo.update(user)

        return user
    
    async def upload_avatar(self, user_id:int, file):
        user = await self.repo.get_by_id(user_id)

        filename = f"user_{user_id}_{file.filename}"
        filepath = os.path.join("media/avatars", filename)

        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if user.avatar and os.path.exists(user.avatar):
            os.remove(user.avatar)

        user.avatar = filepath

        await self.repo.update(user)

        return filepath