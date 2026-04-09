from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
                Room.room_type == room.room_type
            )
        )
        room_search = result.scalar_one_or_none()
        if room_search:
            raise HTTPException(
                status_code=400,
                detail="Комната уже есть в этом отеле!"
            )

        new_room = Room(**room.model_dump())
        self.db.add(new_room)
        await self.db.commit()
        await self.db.refresh(new_room)
        return new_room
    
       
    async def get_all_rooms(self):
        result = await self.db.execute(select(Room))
        rooms = result.scalars().all()
        return rooms
    
    async def search_room_by_id(self, room_id: int):
        result = await self.db.execute(
            select(Room).where(Room.id == room_id)
        )
        room = result.scalar_one_or_none()

        if not room:
            raise HTTPException(status_code=404, detail="Такого hotel нет")
        return room



    async def update_room(self, room_id: int, update_data: dict):
        result = await self.db.execute(select(Room).where(Room.id == room_id))
        room = result.scalar_one_or_none()
        if not room:
            return None


        for key, value in update_data.items():
            setattr(room, key, value)

        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room
    
    
    
    async def delete_room(self , room_id:int):
        result = await self.db.execute(
            select(Room).where(
                Room.id == room_id
            )
        )
        room = result.scalar_one_or_none()

        if not room:
            raise HTTPException(status_code=404, detail="Такой комнаты нет")

        await self.db.delete(room)
        await self.db.commit()
        return {"deleted": True, "id": room_id}
    
    async def search_room(max_price:float,min_prise:float,db:AsyncSession):
        room = select(Room)
        
        if min_prise is not None:
            room = room.where(Room.price >= min_prise)
            
        if max_price is not None:
            room = room.where(Room.price <= max_price)
            
        result = await db.execute(room)
        return result.scalars().all()
    
    
    
        
    
