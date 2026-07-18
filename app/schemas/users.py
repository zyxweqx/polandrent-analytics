from typing import Optional

from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

