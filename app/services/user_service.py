from app.repositories.user_repo import UserRepository
import os
import shutil

from fastapi import HTTPException
from app.auth.auth import verify_password, hash_password

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

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if user.avatar and os.path.exists(user.avatar):
            os.remove(user.avatar)

        user.avatar = filepath

        await self.repo.update(user)

        return filepath
    
    async def change_password(self, user_id:int, data):
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="user not found")
        
        #proveryaem stariy parol
        if not verify_password(data.old_password, user.password):
            raise HTTPException(status_code=400, detail="Wrong old password")
        
        user.password = hash_password(data.new_password)

        await self.repo.db.commit()
        await self.repo.db.refresh(user)

        return {"message":"password update successfull"}

