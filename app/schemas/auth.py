from pydantic import BaseModel, EmailStr

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenSchema(BaseModel):
    access_token: str
    refresh_token:str
    token_type: str = "bearer"


class GoogleRegisterSchema(BaseModel):
    # `credential` from Google Identity Services (id_token)
    id_token: str