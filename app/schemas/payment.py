from pydantic import BaseModel

class CreatePaymentSchema(BaseModel):
    booking_id:int
    provider:str
    amount:float