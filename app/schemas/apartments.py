from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApartmentsBase(BaseModel):
    url: str

    title: str
    city: str
    district: str | None = None

    price: float = Field(gt=0)
    additional_rent: float | None = Field(default=None, ge=0)
    sq_meters: float | None = Field(default=None, gt=0)
    rooms: int | None = Field(default=None, gt=0)
    floor: int | None = None

    pets_allowed: bool | None = None

class ApartmentsCreate(ApartmentsBase):
    pass

class ApartmentsUpdate(ApartmentsBase):
    url: str | None = None

    title: str | None =None
    city: str | None = None
    district: str | None = None

    price: float | None = Field(default=None,gt=0)
    additional_rent: float | None = Field(default=None, ge=0)
    sq_meters: float | None = Field(default=None, gt=0)
    rooms: int | None = Field(default=None, gt=0)
    floor: int | None = None

class ApartmentsResponse(ApartmentsBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
