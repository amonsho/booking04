from pydantic import EmailStr, BaseModel

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id:int
    name:str
    email:EmailStr

    class Config:
        orm_mode = True