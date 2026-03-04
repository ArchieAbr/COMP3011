"""
Investor Router - Analytics endpoints for property investors.
Provides growth forecasting based on market trend data.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Property as PropertyModel, MarketTrend
from ..schemas import GrowthForecast

router = APIRouter(
    prefix="/investor",
    tags=["Investor Analytics"],
)


def extract_postcode_sector(postcode: str) -> str:
    """Extract the outward code (sector) from a UK postcode."""
    parts = postcode.strip().upper().split()
    return parts[0] if parts else postcode[:4]


def extract_region(postcode: str) -> str:
    """Extract region letters from postcode (e.g., 'SW1A' -> 'SW')."""
    sector = extract_postcode_sector(postcode)
    return "".join(c for c in sector if c.isalpha())[:2]


def calculate_growth_rate(prices: list[int]) -> float:
    """Calculate compound annual growth rate from price series."""
    if len(prices) < 2 or prices[0] == 0:
        return 0.0

    years = (len(prices) - 1) / 4  # Quarterly data
    if years <= 0:
        return 0.0

    cagr = ((prices[-1] / prices[0]) ** (1 / years) - 1) * 100
    return round(cagr, 2)


@router.get("/growth-forecast/{postcode}", response_model=GrowthForecast)
def get_growth_forecast(
    postcode: str,
    db: Session = Depends(get_db),
):
    """
    Get price growth forecast for a specific postcode.

    Analyses historical property data and market trends to predict
    future property values for the given postcode area.
    """
    sector = extract_postcode_sector(postcode)
    region = extract_region(postcode)

    # Get properties in this postcode sector
    properties = db.query(PropertyModel).filter(
        PropertyModel.postcode.ilike(f"{sector}%"),
        PropertyModel.status.in_(["for_sale", "sold"]),
    ).all()

    if not properties:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No property data found for postcode {postcode}",
        )

    # Calculate current average price
    prices = [p.price for p in properties if p.price > 0]
    current_avg = int(sum(prices) / len(prices)) if prices else 0

    # Get historical market trends for the region
    trends = db.query(MarketTrend).filter(
        MarketTrend.region.ilike(f"{region}%")
    ).order_by(MarketTrend.quarter).all()

    # Calculate growth rate from trends or use default
    if len(trends) >= 2:
        trend_prices = [t.avg_price for t in trends]
        annual_growth = calculate_growth_rate(trend_prices[-8:])  # Last 2 years
        confidence = "high" if len(trends) >= 8 else "medium"
        data_points = len(trends)
    else:
        # UK average growth rate fallback
        annual_growth = 3.5
        confidence = "low"
        data_points = len(prices)

    # Cap growth rate at reasonable bounds
    annual_growth = max(-10.0, min(15.0, annual_growth))

    # Calculate predictions
    growth_factor_1yr = 1 + (annual_growth / 100)
    growth_factor_5yr = (1 + (annual_growth / 100)) ** 5

    predicted_1yr = int(current_avg * growth_factor_1yr)
    predicted_5yr = int(current_avg * growth_factor_5yr)

    return GrowthForecast(
        postcode=postcode.upper(),
        current_avg_price=current_avg,
        predicted_price_1yr=predicted_1yr,
        predicted_price_5yr=predicted_5yr,
        annual_growth_rate=annual_growth,
        confidence=confidence,
        data_points=data_points,
    )
