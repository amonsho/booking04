from typing import Optional
from pydantic import BaseModel


class HotelCreate(BaseModel):
    name: str
    city: str
    address: str
    description: Optional[str] = None
    photo: str


class HotelRespons(HotelCreate):
    pass


