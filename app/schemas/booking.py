from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

class BookingCreate(BaseModel):
    room_id: int
    date_from: date
    date_to: date
    guests: int = 1

    @field_validator("date_to")
    def check_dates(cls, v, values):
        if "date_from" in values and v <= values["date_from"]:
            raise ValueError("date_to must be greater than date_from")
        return v


class BookingUpdate(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    guests: Optional[int] = None
    status: Optional[str] = None
    
    
class BookingResponse(BaseModel):
    id: int
    user_id: int
    room_id: int

    date_from: date
    date_to: date

    status: str
    total_price: int | None
    guests: int

    class Config:
        from_attributes = True