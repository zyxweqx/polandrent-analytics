from pydantic import BaseModel, ConfigDict, Field, model_validator

from typing import Optional

class RangeValidation:

    _RANGE_FIELDS = (
        ("price_min", "price_max"),
        ("rooms_min", "rooms_max"),
        ("sq_meters_min", "sq_meters_max"),
    )

    @model_validator(mode="after")
    def check_ranges(self):
        for low_name, high_name in self._RANGE_FIELDS:
            low = getattr(self, low_name)
            high = getattr(self, high_name)
            if low is not None and high is not None and low > high:
                raise ValueError(f"{low_name} must not be greater than {high_name}")
        return self

class SubscriptionBase(RangeValidation, BaseModel):
    city: str
    district: Optional[str] = None

    price_min: Optional[float] = Field(default=None,gt=0)
    price_max: Optional[float] = Field(default=None,gt=0)

    rooms_min: Optional[int] = Field(default=None,gt=0)
    rooms_max: Optional[int] = Field(default=None,gt=0)

    sq_meters_min: Optional[float] = Field(default=None,gt=0)
    sq_meters_max: Optional[float] = Field(default=None,gt=0)

    pets_allowed: Optional[bool] = None
    is_owner: Optional[bool] = None
    is_active: Optional[bool] = None

class SubscriptionCreate(SubscriptionBase):
    user_id: int

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class SubscriptionUpdate(RangeValidation, BaseModel):
    city: Optional[str] = None
    district: Optional[str] = None
    price_min: Optional[float] = Field(default=None,gt=0)
    price_max: Optional[float] = Field(default=None,gt=0)
    rooms_min: Optional[int] = Field(default=None,gt=0)
    rooms_max: Optional[int] = Field(default=None,gt=0)
    sq_meters_min: Optional[float] = Field(default=None,gt=0)
    sq_meters_max: Optional[float] = Field(default=None,gt=0)
    pets_allowed: Optional[bool] = None
    is_owner: Optional[bool] = None
    is_active: Optional[bool] = None