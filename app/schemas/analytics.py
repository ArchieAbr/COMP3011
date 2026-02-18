from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class CrimeStatRead(BaseModel):
    id: int
    postcode_sector: str
    month: str
    crime_count: int
    category: str

    model_config = ConfigDict(from_attributes=True)


class MarketTrendRead(BaseModel):
    id: int
    region: str
    quarter: str
    avg_price: int

    model_config = ConfigDict(from_attributes=True)


class AreaMetricRead(BaseModel):
    id: int
    postcode_sector: str
    period: str
    safety_score: Optional[int] = Field(default=None)
    affordability_index: Optional[int] = Field(default=None)
    yield_estimate: Optional[float] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)
