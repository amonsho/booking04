from pydantic import BaseModel

class ReviewCreate(BaseModel):
    hotel_id:int
    rating:int
    comment:str

class ReviewResponse(BaseModel):
    id:int
    user_id:int
    hotel_id:int
    rating:int
    comment:str

    class Config:
        from_attributes = True