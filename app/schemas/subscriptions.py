from pydantic import BaseModel, ConfigDict

from typing import Optional

class SubscriptionBase(BaseModel):
    city: str
    district: Optional[str] = None

    price_min: Optional[float] = None
    price_max: Optional[float] = None

    rooms_min: Optional[int] = None
    rooms_max: Optional[int] = None

    sq_meters_min: Optional[float] = None
    sq_meters_max: Optional[float] = None

    pets_allowed: Optional[bool] = None
    is_owner: Optional[bool] = None
    is_active: Optional[bool] = None

class SubscriptionCreate(SubscriptionBase):
    user_id: int

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)