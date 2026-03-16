from sqlalchemy import select
from fastapi import HTTPException

from app.models.user import User
from app.models.enums import UserRole
from app.repositories.user_repo import UserRepository

class AdminSerivce:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_all_users(self):
        users = await self.repo.get_all()
        return users
    
    async def delete_user(self, user_id: int):
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        await self.repo.delete(user)
        return {"message": "User deleted"}
    
    async def change_user_role(self, user_id:int, role:UserRole):
        user = await self.repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        user.role = role

        await self.repo.update(user)
        return user