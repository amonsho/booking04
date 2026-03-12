from pydantic import BaseModel

class ProfileUpdate(BaseModel):
    name: str | None = None
    