from typing import Optional
from pydantic import BaseModel

class HotelCreate(BaseModel):
    name: str
    city: str
    country:str
    address: str
    description: Optional[str] = None
    photo: str  
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HotelResponse(BaseModel):
    id: int
    name: str
    city: str
    country:str
    address: str
    description: Optional[str] = None
    photo: Optional[str] = None 
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    model_config = {"from_attributes": True}


class HotelUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    photo: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None