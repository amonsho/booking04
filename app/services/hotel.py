from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate


# доболения Hotel 
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

class HotelService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_hotel(self, hotel: HotelCreate):

        result = await self.db.execute(
            select(Hotel).where(
                Hotel.name == hotel.name,
                Hotel.city == hotel.city
            )
        )

        hotel_search = result.scalar_one_or_none()

        if hotel_search:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отель уже существует в этом городе"
            )

        new_hotel = Hotel(**hotel.model_dump())

        self.db.add(new_hotel)
        await self.db.commit()
        await self.db.refresh(new_hotel)

        return new_hotel
    
    

    
