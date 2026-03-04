"""
Pydantic schemas for analytics responses.
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ============== Database Model Schemas ==============

class CrimeStatRead(BaseModel):
    """Crime statistics for a postcode sector."""

    id: int
    postcode_sector: str
    month: str
    crime_count: int
    category: str

    model_config = ConfigDict(from_attributes=True)


class MarketTrendRead(BaseModel):
    """Market trend data for a region."""

    id: int
    region: str
    quarter: str
    avg_price: int

    model_config = ConfigDict(from_attributes=True)


class AreaMetricRead(BaseModel):
    """Aggregated metrics for an area."""

    id: int
    postcode_sector: str
    period: str
    safety_score: Optional[int] = Field(default=None)
    affordability_index: Optional[int] = Field(default=None)
    yield_estimate: Optional[float] = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


# ============== Investor Analytics Schemas ==============

class GrowthForecast(BaseModel):
    """Growth forecast response for a postcode."""

    postcode: str
    current_avg_price: int = Field(..., description="Current average price in GBP")
    predicted_price_1yr: int = Field(..., description="Predicted price in 1 year")
    predicted_price_5yr: int = Field(..., description="Predicted price in 5 years")
    annual_growth_rate: float = Field(..., description="Annual growth rate (%)")
    confidence: str = Field(..., description="high, medium, or low")
    data_points: int = Field(..., description="Number of data points used")


class YieldHotspot(BaseModel):
    """Single yield hotspot entry."""

    postcode_sector: str
    avg_property_price: int
    avg_monthly_rent: int
    gross_yield: float = Field(..., description="Gross rental yield (%)")
    properties_count: int


class YieldHotspotsResponse(BaseModel):
    """List of top yield hotspots."""

    region: Optional[str] = None
    hotspots: list[YieldHotspot]
    generated_at: str


class MarketTrendResponse(BaseModel):
    """Regional market trend data point."""

    region: str
    quarter: str
    avg_price: int
    price_change_pct: Optional[float] = None


class RegionalTrendsResponse(BaseModel):
    """Multiple quarters of market trends."""

    region: str
    trends: list[MarketTrendResponse]
