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
                Hotel.city == hotel.city,
                Hotel.is_deleted == False
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
    
    
    async def get_all_hotel(self, limit: int = 10, offset: int = 0, q_city: str | None = None, q_country: str | None = None):
        query = select(Hotel).where(Hotel.is_deleted == False)
        if q_city:
            query = query.where(Hotel.city.ilike(f"%{q_city}%"))
        if q_country:
            query = query.where(Hotel.country.ilike(f"%{q_country}%"))
        
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        hotels = result.scalars().all()
        return hotels
    
    async def search_hotel_by_id(self, hotel_id: int):
        result = await self.db.execute(
            select(Hotel).where(Hotel.id == hotel_id, Hotel.is_deleted == False)
        )
        hotel = result.scalar_one_or_none()

        if not hotel:
            raise HTTPException(status_code=404, detail="Такого hotel нет")

        return hotel

    async def _get_hotel_any(self, hotel_id: int):
        """Internal helper to get hotel regardless of is_deleted status"""
        result = await self.db.execute(
            select(Hotel).where(Hotel.id == hotel_id)
        )
        return result.scalar_one_or_none()

    async def get_deleted_hotels(self, limit: int = 10, offset: int = 0):
        result = await self.db.execute(
            select(Hotel).where(Hotel.is_deleted == True).limit(limit).offset(offset)
        )
        return result.scalars().all()

    async def restore_hotel(self, hotel_id: int):
        hotel = await self._get_hotel_any(hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        
        hotel.is_deleted = False
        await self.db.commit()
        await self.db.refresh(hotel)
        return hotel

    async def update_hotel(self, hotel_id:int , hotel_data:HotelUpdate):
        result = await self.db.execute(
            select(Hotel).where(
                Hotel.id == hotel_id,
                Hotel.is_deleted == False
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
        hotel = await self.get_hotel_by_id(hotel_id)
        if not hotel:
            return False
        hotel.is_deleted = True
        await self.db.commit()
        return True
    
    async def search_hotel(self, q_hotel:str):
        from sqlalchemy import or_
        query = select(Hotel).where(
            Hotel.is_deleted == False,
            or_(
                Hotel.name.ilike(f'%{q_hotel}%'),
                Hotel.city.ilike(f'%{q_hotel}%'),
                Hotel.country.ilike(f'%{q_hotel}%'),
                Hotel.address.ilike(f'%{q_hotel}%')
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def autocomplete_city(self, q_city: str):
        city = select(Hotel).where(Hotel.city.ilike(f'%{q_city}%'), Hotel.is_deleted == False)
        result = await self.db.execute(city)
        return result.scalars().all()
    
    async def autocomplete_country(self, q_country: str):
        country = select(Hotel).where(Hotel.country.ilike(f'%{q_country}%'), Hotel.is_deleted == False)
        
        result = await self.db.execute(country)
        return result.scalars().all()