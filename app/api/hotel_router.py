from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.hotel import HotelCreate, HotelResponse,HotelUpdate
from app.services.hotel import HotelService
import os
import uuid
import aiofiles
from app.models.hotel import Hotel
from app.models.room import Room
from sqlalchemy import func,select

from app.auth.dependencies import get_current_user, get_admin_user

hotel_router = APIRouter(prefix="/hotel", tags=["Hotel"])

UPLOAD_DIR = "media"

os.makedirs(UPLOAD_DIR, exist_ok=True)

#----------------------------------------------------
@hotel_router.post("/", response_model=HotelResponse)
async def add_hotel(
    name: str = Form(...),
    city: str = Form(...),
    address: str = Form(...),
    description: str = Form(None),
    photo: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user)
):

    file_name = f"{uuid.uuid4()}_{photo.filename}"
    file_location = os.path.join(UPLOAD_DIR, file_name)

    async with aiofiles.open(file_location, 'wb')  as buffer:
        # Must await the write, otherwise file may be created as 0 bytes.
        await buffer.write(await photo.read())

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
async def get_all_hotels(db: AsyncSession = Depends(get_db), user = Depends(get_current_user)):
    service = HotelService(db)
    hotels = await service.get_all_hotel()
    return hotels


@hotel_router.get('/{hotel_id}',response_model=HotelResponse)
async def get_by_id(hotel_id:int,db:AsyncSession = Depends(get_db), user = Depends(get_current_user)):
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
    service: HotelService = Depends(HotelService.get_hotel_service),
    admin = Depends(get_admin_user)
):

    update_data = {}

    if name is not None:
        update_data["name"] = name
    if city is not None:
        update_data["city"] = city
    if address is not None:
        update_data["address"] = address
    if description is not None:
        update_data["description"] = description



    if photo:
        file_name = f"{uuid.uuid4()}_{photo.filename}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as buffer:
            buffer.write(await photo.read())

        update_data["photo"] = file_name 

    hotel_data = HotelUpdate(**update_data)

    return await service.update_hotel(hotel_id, hotel_data)


@hotel_router.delete("/{hotel_id}")
async def delete_hotel(
    hotel_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user)
):
    service = HotelService(db)

    await service.delete_hotel(hotel_id)

    return {"message": "Hotel deleted successfully"}



@hotel_router.get("/reports/hotels_count")
async def hotels_count(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.count(Hotel.id)))
    count = result.scalar()
    return {"hotels_count": count}

@hotel_router.get('search_hotels/')
async def  search_hotels(q:str,db:AsyncSession = Depends(get_db)):
    hotels = await HotelService.search_hotel(q,db)
    return {"results": hotels}