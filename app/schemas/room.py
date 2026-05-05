from pydantic import BaseModel, field_validator
from typing import Optional, List, Any

class RoomBase(BaseModel):
    hotel_id: int
    room_type: str
    number_room: int
    price: float
    wifi: bool
    photos: List[str] = []
    is_available: bool = True

    @field_validator("photos", mode="before")
    @classmethod
    def parse_photos(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            if not v:
                return []
            return [p.strip() for p in v.split(";") if p.strip()]
        return v or []
    
class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    hotel: Optional['HotelResponse'] = None
    model_config = {"from_attributes": True}

class RoomUpdate(BaseModel):
    hotel_id: Optional[int] = None
    room_type: Optional[str] = None
    number_room: Optional[int] = None
    price: Optional[float] = None
    wifi: Optional[bool] = None
    photos: Optional[list[str]] = None
    
    model_config = {"from_attributes": True}

from app.schemas.hotel import HotelResponse
RoomResponse.model_rebuild()