from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class ApartmentsBase(BaseModel):
    url: str

    title: str
    city: str
    district: Optional[str] = None

    price: float = Field(gt=0)
    additional_rent: Optional[float] = Field(default=None, ge=0)
    sq_meters: Optional[float] = Field(default=None, gt=0)
    rooms: Optional[int] = Field(default=None, gt=0)
    floor: Optional[int] = None

    pets_allowed: Optional[bool] = None

class ApartmentsCreate(ApartmentsBase):
    pass

class ApartmentsUpdate(ApartmentsBase):
    url: Optional[str] = None

    title: Optional[str] =None
    city: Optional[str] = None
    district: Optional[str] = None

    price: Optional[float] = Field(default=None,gt=0)
    additional_rent: Optional[float] = Field(default=None, ge=0)
    sq_meters: Optional[float] = Field(default=None, gt=0)
    rooms: Optional[int] = Field(default=None, gt=0)
    floor: Optional[int] = None

class ApartmentsResponse(ApartmentsBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
