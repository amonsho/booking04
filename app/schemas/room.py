from pydantic import BaseModel
from typing import Optional

class RoomBase(BaseModel):
    hotel_id: int
    room_type: str
    number_room:int
    price: float
    wifi: bool
    photo: str  
    
class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    model_config = {"from_attributes": True}

class RoomUpdate(BaseModel):
    hotel_id: Optional[int] = None
    room_type: Optional[str] = None
    number_room: Optional[int] = None
    price: Optional[float] = None
    wifi: Optional[bool] = None
    photo: Optional[str] = None
    
    model_config = {"from_attributes": True}