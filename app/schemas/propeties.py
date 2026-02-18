from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PropertyBase(BaseModel):
    postcode: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)
    price: int
    property_type: str = Field(..., min_length=1)
    bedrooms: int
    status: str = Field(..., min_length=1)


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    postcode: Optional[str] = None
    address: Optional[str] = None
    price: Optional[int] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    status: Optional[str] = None


class PropertyRead(PropertyBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
