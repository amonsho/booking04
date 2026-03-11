from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status, Depends

from app.models.hotel import Hotel
from app.schemas.hotel import HotelCreate
from app.db.session import get_db


async def create_hotel(hotel: HotelCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
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

    db.add(new_hotel)
    await db.commit()
    await db.refresh(new_hotel)

    return new_hotel
   
    
    
