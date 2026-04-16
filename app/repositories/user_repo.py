from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id:int):
        result = await self.db.execute(select(User).where(User.id == user_id, User.is_deleted == False))
        return result.scalar_one_or_none()

    async def get_by_id_any(self, user_id: int):
        """Internal helper to get user regardless of is_deleted status"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_google_id(self, google_id:str):
        result = await self.db.execute(select(User).where(User.google_id == google_id, User.is_deleted == False))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email:str):
        result = await self.db.execute(select(User).where(User.email == email, User.is_deleted == False))
        return result.scalar_one_or_none()
    
    async def get_all(self):
        result = await self.db.execute(select(User).where(User.is_deleted == False))
        return result.scalars().all()

    async def get_deleted_all(self):
        result = await self.db.execute(select(User).where(User.is_deleted == True))
        return result.scalars().all()
    
    async def update(self, user:User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user:User):
        user.is_deleted = True
        await self.db.commit()

    async def restore(self, user_id: int):
        user = await self.get_by_id_any(user_id)
        if user:
            user.is_deleted = False
            await self.db.commit()
            await self.db.refresh(user)
        return user