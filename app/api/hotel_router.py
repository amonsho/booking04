from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.hotel import HotelCreate, HotelResponse,HotelUpdate
from app.services.hotel import HotelService
import os
import uuid
import aiofiles

hotel_router = APIRouter(prefix="/hotel", tags=["Hotel"])

UPLOAD_DIR = "media"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@hotel_router.post("/", response_model=HotelResponse)
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

    async with aiofiles.open(file_location, 'wb')  as buffer:
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


@hotel_router.get("/get_all", response_model=list[HotelResponse])
async def get_all_hotels(db: AsyncSession = Depends(get_db)):
    service = HotelService(db)
    hotels = await service.get_all_hotel()
    return hotels


@hotel_router.get('/{hotel_id}',response_model=HotelResponse)
async def get_by_id(hotel_id:int,db:AsyncSession = Depends(get_db)):
    service = HotelService(db)

    hotel = await service.search_hotel_by_id(hotel_id)

    return hotel 


@hotel_router.patch("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(
    hotel_id: int,
    name: str | None = Form(None),
    city: str | None = Form(None),
    address: str | None = Form(None),
    description: str | None = Form(None),
    photo: UploadFile | None = File(None),
    service: HotelService = Depends(HotelService.get_hotel_service)
):

    photo_path = None
    if photo:
        file_name = f"{uuid.uuid4()}_{photo.filename}"
        file_location = os.path.join(UPLOAD_DIR, file_name)
        with open(file_location, "wb") as buffer:
            buffer.write(await photo.read())
        photo_path = file_location

    hotel_data = HotelUpdate(
        name=name,
        city=city,
        address=address,
        description=description,
        photo=photo_path
    )

    return await service.update_hotel(hotel_id, hotel_data)


@hotel_router.delete('/{hotel_id}')
async def delete_hotel(hotel_id:int , db : AsyncSession = Depends(get_db)):
    
    service = HotelService(db)
    hotel = service.delete_hotel(hotel_id)
    
    return {f'{hotel} удален'}


