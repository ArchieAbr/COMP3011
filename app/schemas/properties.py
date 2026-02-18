from pydantic import BaseModel

class PropertyBase(BaseModel):
    postcode: str
    address: str
    price: int
    property_type: str
    bedrooms: int
    status: str

class PropertyCreate(PropertyBase):
    pass

class Property(PropertyBase):
    id: int

    class Config:
        from_attributes = True