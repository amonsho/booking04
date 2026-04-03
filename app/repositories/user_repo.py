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
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_google_id(self, google_id:str):
        result = await self.db.execute(select(User).where(User.google_id == google_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email:str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_all(self):
        result = await self.db.execute(select(User))
        return result.scalars().all()
    
    async def update(self, user:User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user:User):
        await self.db.delete(user)
        await self.db.commit()