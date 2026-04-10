from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status ,Depends
import os
from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate,HotelUpdate
from app.db.session import get_db

UPLOAD_DIR = "media/hotel"

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
    
    
    async def get_all_hotel(self, limit: int = 100, offset: int = 0, city: str | None = None, country: str | None = None):
        query = select(Hotel)
        if city:
            query = query.where(Hotel.city.ilike(f"%{city}%"))
        
        # We only have city/address fields, so we filter by city if either is provided
        # or we could search for country in the address if we had that field.
        
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        hotels = result.scalars().all()
        return hotels
    
    async def search_hotel_by_id(self, hotel_id: int):
        result = await self.db.execute(
            select(Hotel).where(Hotel.id == hotel_id)
        )
        hotel = result.scalar_one_or_none()

        if not hotel:
            raise HTTPException(status_code=404, detail="Такого hotel нет")

        return hotel
    async def update_hotel(self, hotel_id:int , hotel_data:HotelUpdate):
        result = await self.db.execute(
            select(Hotel).where(
                Hotel.id == hotel_id 
            )
        )
        
        hotel = result.scalar_one_or_none()
        
        if not hotel : 
            raise HTTPException(status_code=404,detail="Такова hotel нет !!!")
        
        for field , value in hotel_data.model_dump(exclude_unset=True).items():
            setattr(hotel,field,value)
            
        try: 
            await self.db.commit()
            await self.db.refresh(hotel)
        except Exception:
            await self.db.rollback()
            raise
        
        return hotel
    

    def get_hotel_service(db: AsyncSession = Depends(get_db)):
        return HotelService(db)


    async def delete_hotel(self, hotel_id: int):
        result = await self.db.execute(
            select(Hotel).where(Hotel.id == hotel_id)
     )
        hotel = result.scalar_one_or_none()

        if not hotel:
            raise HTTPException(status_code=404, detail="Такого hotel нет!")


        if hotel.photo:
            file_path = os.path.join(UPLOAD_DIR, hotel.photo)
            if os.path.exists(file_path):
                os.remove(file_path)

        await self.db.delete(hotel)
        await self.db.commit()

        return {"deleted": True}
    
    async def search_hotel(q_hotel:str,db:AsyncSession):
        from sqlalchemy import or_
        query = select(Hotel).where(
            or_(
                Hotel.name.ilike(f'%{q_hotel}%'),
                Hotel.city.ilike(f'%{q_hotel}%'),
                Hotel.address.ilike(f'%{q_hotel}%')
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    