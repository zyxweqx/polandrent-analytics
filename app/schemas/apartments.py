from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class ApartmentsBase(BaseModel):
    url: str

    title: str
    city: str
    district: Optional[str] = None

    price: float
    additional_rent: Optional[float] = None
    sq_meters: Optional[float] = None
    rooms: Optional[int] = None
    floor: Optional[int] = None

    pets_allowed: Optional[bool] = None

class ApartmentsCreate(ApartmentsBase):
    pass

class ApartmentsResponse(ApartmentsBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
