from pydantic import BaseModel, model_validator
from datetime import date
from typing import Optional

class BookingCreate(BaseModel):
    room_id: int
    date_from: date
    date_to: date
    guests: int = 1

    @model_validator(mode="after")
    def check_dates(self):
        if self.date_to <= self.date_from:
            raise ValueError("date_to must be greater than date_from")
        return self



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
    model_config = {"from_attributes": True}