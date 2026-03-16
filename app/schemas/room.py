from pydantic import BaseModel
from typing import Optional


class RoomBase(BaseModel):
    hotel_id: int
    room_type: str
    price: float
    wifi: bool


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int

    class Config:
        orm_mode = True


class RoomUpdate(BaseModel):
    hotel_id: Optional[int] = None
    room_type: Optional[str] = None
    price: Optional[float] = None
    wifi: Optional[bool] = None