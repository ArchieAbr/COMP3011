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


# ============== Living/Relocator Analytics Schemas ==============

class SafetyScoreResponse(BaseModel):
    """Safety score for a postcode area."""

    postcode: str
    safety_score: int = Field(..., ge=0, le=100, description="0-100 score (higher = safer)")
    crime_count_6m: int = Field(..., description="Total crimes in last 6 months")
    top_crime_categories: list[str] = Field(..., description="Most common crime types")
    rating: str = Field(..., description="very_safe, safe, moderate, caution, high_risk")
    data_months: int = Field(..., description="Months of data used")


class AffordabilityResponse(BaseModel):
    """Affordability analysis for a postcode area."""

    postcode: str
    avg_property_price: int
    avg_monthly_rent: int
    price_to_rent_ratio: float = Field(..., description="Property price / annual rent")
    affordability_index: int = Field(..., ge=0, le=100, description="0-100 (higher = more affordable)")
    rating: str = Field(..., description="very_affordable, affordable, moderate, expensive, very_expensive")
    properties_analysed: int


class AreaSummary(BaseModel):
    """Summary of a single area for comparison."""

    postcode: str
    safety_score: int
    affordability_index: int
    avg_price: int
    avg_rent: int
    properties_count: int


class CompareAreasResponse(BaseModel):
    """Comparison of multiple areas."""

    areas: list[AreaSummary]
    recommended: Optional[str] = Field(None, description="Best postcode based on criteria")
