from pydantic import EmailStr, BaseModel, field_validator,model_validator
import re
from app.models.enums import UserRole

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    password2: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Пароль должен состоять как минимум из 6 символов.")
        
        if not re.search(r"[A-za-z]", value):
            raise ValueError("Пароль должен содержать букву.")
        
        if not re.search(r"\d", value):
            raise ValueError("Пароль должен содержать цифру.")
        
        return value
    
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password2:
            raise ValueError("Пароли не совпадают")
        return self
        
class UserRead(BaseModel):
    id:int
    name:str
    email:EmailStr
    role: UserRole
    avatar: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    google_id: str | None = None
    is_verified: bool = False

    model_config = {"from_attributes": True}

class ChangePasswordSchema(BaseModel):
    old_password:str
    new_password:str
    new_password2:str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Пароль должен состоять как минимум из 6 символов.")
        
        if not re.search(r"[A-za-z]", value):
            raise ValueError("Пароль должен содержать букву.")
        
        if not re.search(r"\d", value):
            raise ValueError("Пароль должен содержать цифру.")
        
        return value
    
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.new_password != self.new_password2:
            raise ValueError("Пароль не совпадают")
        return self

class UserRoleUpdate(BaseModel):
    role: UserRole