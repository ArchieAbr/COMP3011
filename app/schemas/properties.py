"""
Pydantic schemas for Property CRUD operations.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PropertyBase(BaseModel):
    """Base schema for property data."""

    postcode: str = Field(..., min_length=2, max_length=10, description="UK postcode")
    address: str = Field(..., min_length=1, max_length=255, description="Full address")
    price: int = Field(..., ge=0, description="Price in GBP")
    property_type: str = Field(..., description="Type: house, flat, terraced, etc.")
    bedrooms: int = Field(..., ge=0, le=20, description="Number of bedrooms")
    status: str = Field(..., description="Status: for_sale, for_rent, sold, let")


class PropertyCreate(PropertyBase):
    """Schema for creating a new property."""

    pass


class PropertyUpdate(BaseModel):
    """Schema for updating a property (all fields optional)."""

    postcode: Optional[str] = Field(None, min_length=2, max_length=10)
    address: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[int] = Field(None, ge=0)
    property_type: Optional[str] = None
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    status: Optional[str] = None


class PropertyRead(PropertyBase):
    """Schema for property response with ID."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class PropertyList(BaseModel):
    """Paginated list of properties."""

    total: int
    page: int
    per_page: int
    properties: list[PropertyRead]