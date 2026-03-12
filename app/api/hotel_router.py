from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.hotel import HotelCreate, HotelRespons
from app.services.hotel import HotelService

hotel_router = APIRouter(prefix="/hotel", tags=["Hotel"])

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.hotel import HotelCreate, HotelRespons
from app.services.hotel import HotelService,HorelSearch

import os
import uuid

hotel_router = APIRouter(prefix="/hotel", tags=["Hotel"])

UPLOAD_DIR = "media"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@hotel_router.post("/", response_model=HotelRespons)
async def add_hotel(
    name: str = Form(...),
    city: str = Form(...),
    address: str = Form(...),
    description: str = Form(None),
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):

    file_name = f"{uuid.uuid4()}_{photo.filename}"
    file_location = os.path.join(UPLOAD_DIR, file_name)

    with open(file_location, "wb") as buffer:
        buffer.write(await photo.read())

    hotel_data = HotelCreate(
        name=name,
        city=city,
        address=address,
        description=description,
        photo=file_location
    )

    service = HotelService(db)

    return await service.create_hotel(hotel_data)



@hotel_router.get('/{hotel_id}')
async def get_by_id(hotel_id:int,db:AsyncSession = Depends(get_db)):
    service = HorelSearch(db)

    hotel = await service.search_hotel_by_id(hotel_id)

    return hotel 
    
    