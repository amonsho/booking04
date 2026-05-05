from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.room import Room
from app.schemas.room import RoomCreate , RoomUpdate



class RoomService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_room(self, room: RoomCreate):
        result = await self.db.execute(
            select(Room).where(
                Room.hotel_id == room.hotel_id,
                Room.room_type == room.room_type,
                Room.number_room == room.number_room,
                Room.is_deleted == False
            )
        )
        room_search = result.scalar_one_or_none()
        if room_search:
            raise HTTPException(
                status_code=400,
                detail="Комната с таким номером и типом уже есть в этом отеле!"
            )

        room_dict = room.model_dump()
        if isinstance(room_dict.get("photos"), list):
            room_dict["photos"] = ";".join(room_dict["photos"])
            
        new_room = Room(**room_dict)
        self.db.add(new_room)
        await self.db.commit()
        await self.db.refresh(new_room, attribute_names=["hotel"])
        
        # Load hotel explicitly after commit/refresh
        result = await self.db.execute(
            select(Room).options(selectinload(Room.hotel)).where(Room.id == new_room.id)
        )
        new_room = result.scalar_one()
        
        # Convert back for response
        if new_room.photos:
            new_room.photos = new_room.photos.split(";")
        else:
            new_room.photos = []
        return new_room
    
       
    async def get_all_rooms(self, hotel_id: int = None):
        query = select(Room).options(selectinload(Room.hotel)).where(Room.is_deleted == False)
        if hotel_id is not None:
            query = query.where(Room.hotel_id == hotel_id)
            
        result = await self.db.execute(query)
        rooms = result.scalars().all()
        for room in rooms:
            if room.photos:
                room.photos = room.photos.split(";")
            else:
                room.photos = []
        return rooms
    
    async def search_room_by_id(self, room_id: int):
        result = await self.db.execute(
            select(Room).options(selectinload(Room.hotel)).where(Room.id == room_id, Room.is_deleted == False)
        )
        room = result.scalar_one_or_none()

        if not room:
            raise HTTPException(status_code=404, detail="Такой комнаты нет")
        
        if room.photos:
            room.photos = room.photos.split(";")
        else:
            room.photos = []
        return room

    async def _get_room_any(self, room_id: int):
        """Internal helper to get room regardless of is_deleted status"""
        result = await self.db.execute(
            select(Room).where(Room.id == room_id)
        )
        return result.scalar_one_or_none()

    async def get_deleted_rooms(self, limit: int = 100, offset: int = 0):
        result = await self.db.execute(
            select(Room).options(selectinload(Room.hotel)).where(Room.is_deleted == True).limit(limit).offset(offset)
        )
        rooms = result.scalars().all()
        for room in rooms:
            if room.photos:
                room.photos = room.photos.split(";")
            else:
                room.photos = []
        return rooms

    async def restore_room(self, room_id: int):
        room = await self._get_room_any(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        room.is_deleted = False
        await self.db.commit()
        
        # Reload with hotel relationship
        result = await self.db.execute(
            select(Room).options(selectinload(Room.hotel)).where(Room.id == room_id)
        )
        room = result.scalar_one()
        
        if room.photos:
            room.photos = room.photos.split(";")
        else:
            room.photos = []
        return room



    async def update_room(self, room_id: int, update_data: dict):
        result = await self.db.execute(select(Room).where(Room.id == room_id))
        room = result.scalar_one_or_none()
        if not room:
            return None

        for key, value in update_data.items():
            if key == "photos" and isinstance(value, list):
                value = ";".join(value)
            setattr(room, key, value)

        self.db.add(room)
        await self.db.commit()
        
        # Reload with hotel relationship
        result = await self.db.execute(
            select(Room).options(selectinload(Room.hotel)).where(Room.id == room_id)
        )
        room = result.scalar_one()
        
        if room.photos:
            room.photos = room.photos.split(";")
        else:
            room.photos = []
        return room
    
    
    
    async def delete_room(self , room_id:int):
        result = await self.db.execute(
            select(Room).where(
                Room.id == room_id,
                Room.is_deleted == False
            )
        )
        room = result.scalar_one_or_none()

        if not room:
            raise HTTPException(status_code=404, detail="Такой комнаты нет")

        room.is_deleted = True
        await self.db.commit()
        return {"deleted": True, "id": room_id}
    
    @staticmethod
    async def search_room(min_price: float, max_price: float, db: AsyncSession):
        query = select(Room).where(Room.is_deleted == False)
        
        if min_price is not None:
            query = query.where(Room.price >= min_price)
            
        if max_price is not None:
            query = query.where(Room.price <= max_price)
            
        result = await db.execute(query)
        return result.scalars().all()
