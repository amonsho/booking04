from fastapi import APIRouter, Depends, UploadFile, File, Form ,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.room import RoomCreate, RoomResponse ,RoomUpdate
from app.services.room_service import RoomService
import uuid
import os
import aiofiles
from app.auth.dependencies import get_admin_user

room_router = APIRouter(prefix="/rooms", tags=["Rooms"])

UPLOAD_DIR = "media/room"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@room_router.post("/", response_model=RoomResponse)
async def create_room(
    hotel_id: int = Form(...),
    room_type: str = Form(...),
    number_room: str = Form(...),
    price: float = Form(description="Цена должна быть больше 0"),
    wifi: bool = Form(...),
    photos: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user),
):
    if len(photos) > 10:
        raise HTTPException(status_code=400, detail="Максимум 10 фотографий")

    saved_photos = []
    for photo in photos:
        file_name = f"{uuid.uuid4()}_{photo.filename}"
        file_path = f"{UPLOAD_DIR}/{file_name}"

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await photo.read())
        saved_photos.append(file_path)

    room_data = RoomCreate(
        hotel_id=hotel_id,
        room_type=room_type,
        price=price,
        wifi=wifi,
        photos=saved_photos,
        number_room=number_room
    )

    service = RoomService(db)
    return await service.create_room(room_data)


@room_router.get("/", response_model=list[RoomResponse])
async def get_all_rooms(
    hotel_id: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    service = RoomService(db)
    return await service.get_all_rooms(hotel_id=hotel_id)


@room_router.get("/deleted", response_model=list[RoomResponse])
async def get_deleted_rooms(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user)
):
    service = RoomService(db)
    return await service.get_deleted_rooms(limit=limit, offset=offset)


@room_router.get("/search_room")
async def search_room(min_price: float, max_price: float, db: AsyncSession = Depends(get_db)):
    rooms = await RoomService.search_room(min_price, max_price, db)
    return {"results": rooms}


@room_router.post("/{room_id}/restore", response_model=RoomResponse)
async def restore_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user)
):
    service = RoomService(db)
    return await service.restore_room(room_id)


@room_router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = RoomService(db)
    return await service.search_room_by_id(room_id)


@room_router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int,
    room_type: str = Form(None),
    price: float = Form(None),
    wifi: bool = Form(None),
    hotel_id: int = Form(None),
    number_room: str = Form(None),
    photos: list[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user),
):
    service = RoomService(db)

    update_data = {}

    if room_type is not None:
        update_data["room_type"] = room_type
    if price is not None:
        update_data["price"] = price
    if wifi is not None:
        update_data["wifi"] = wifi
    if hotel_id is not None:
        update_data["hotel_id"] = hotel_id
    if number_room is not None:
        update_data["number_room"] = number_room

    if photos is not None:
        if len(photos) > 10:
            raise HTTPException(status_code=400, detail="Максимум 10 фотографий")
            
        saved_photos = []
        for photo in photos:
            file_name = f"{uuid.uuid4()}_{photo.filename}"
            file_path = os.path.join(UPLOAD_DIR, file_name)
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(await photo.read())
            saved_photos.append(file_path)
            
        update_data["photos"] = saved_photos

    updated_room = await service.update_room(room_id, update_data)
    if not updated_room:
        raise HTTPException(status_code=404, detail="Комната не найдена")

    return updated_room


@room_router.delete("/{room_id}")
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    admin = Depends(get_admin_user),
):
    service = RoomService(db)
    return await service.delete_room(room_id)
    
