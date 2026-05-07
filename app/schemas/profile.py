from pydantic import BaseModel

class ProfileUpdate(BaseModel):
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    