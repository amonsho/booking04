from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.hotel import HotelCreate
from app.services.hotel import create_hotel
import uuid
import os

hotel = APIRouter(prefix='/hotel', tags=['hotel'])

@hotel.post('/hotel')
async def add_hotel(
    name: str = Form(...),
    city: str = Form(...),
    address: str = Form(...),
    description: str = Form(None),
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    
    
    os.makedirs("media", exist_ok=True)

    file_extension = photo.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_location = f"media/{file_name}"
  
    with open(file_location, "wb") as buffer:
        buffer.write(await photo.read())

    hotel_data = HotelCreate(
        name=name,
        city=city,
        address=address,
        description=description,
        photo=file_location
    )

    new_hotel = await create_hotel(hotel_data, db)

    hotel_out = {
        "id": new_hotel.id,
        "name": new_hotel.name,
        "city": new_hotel.city,
        "address": new_hotel.address,
        "description": new_hotel.description,
        "photo": new_hotel.photo
    }

    return {
        "message": "Hotel создан",
        "hotel": hotel_out
    }