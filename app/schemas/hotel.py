from pydantic import BaseModel

class HotelCreate(BaseModel):
    name: str
    city: str
    address: str
    description: str
    

class HotelRespons(HotelCreate):
    pass 


