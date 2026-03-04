"""
Investor Router - Analytics endpoints for property investors.
Provides growth forecasting based on market trend data.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Property as PropertyModel, MarketTrend
from ..schemas import (
    GrowthForecast,
    MarketTrendResponse,
    RegionalTrendsResponse,
    YieldHotspot,
    YieldHotspotsResponse,
)

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


@router.get("/yield-hotspots", response_model=YieldHotspotsResponse)
def get_yield_hotspots(
    region: Optional[str] = Query(None, description="Filter by region (e.g., 'SW', 'NW')"),
    limit: int = Query(10, ge=1, le=50, description="Number of hotspots to return"),
    db: Session = Depends(get_db),
):
    """
    Get top rental yield hotspots.

    Returns postcode sectors ranked by gross rental yield,
    optionally filtered by region.
    """
    # Build base query for properties with rent data
    query = db.query(
        func.left(PropertyModel.postcode, 4).label("postcode_sector"),
        func.avg(PropertyModel.price).label("avg_price"),
        func.avg(PropertyModel.rent_pcm).label("avg_rent"),
        func.count(PropertyModel.id).label("count"),
    ).filter(
        PropertyModel.price > 0,
        PropertyModel.rent_pcm > 0,
    )

    if region:
        query = query.filter(PropertyModel.postcode.ilike(f"{region.upper()}%"))

    # Group by postcode sector
    results = query.group_by(
        func.left(PropertyModel.postcode, 4)
    ).having(
        func.count(PropertyModel.id) >= 3  # Minimum sample size
    ).all()

    # Calculate yields and sort
    hotspots = []
    for row in results:
        avg_price = int(row.avg_price)
        avg_rent = int(row.avg_rent)

        if avg_price > 0:
            gross_yield = round((avg_rent * 12 / avg_price) * 100, 2)
            hotspots.append(
                YieldHotspot(
                    postcode_sector=row.postcode_sector,
                    avg_property_price=avg_price,
                    avg_monthly_rent=avg_rent,
                    gross_yield=gross_yield,
                    properties_count=row.count,
                )
            )

    # Sort by yield descending and limit
    hotspots.sort(key=lambda x: x.gross_yield, reverse=True)
    hotspots = hotspots[:limit]

    return YieldHotspotsResponse(
        region=region.upper() if region else None,
        hotspots=hotspots,
        generated_at=datetime.utcnow().isoformat() + "Z",
    )


@router.get("/market-trends/{region}", response_model=RegionalTrendsResponse)
def get_market_trends(
    region: str,
    quarters: int = Query(8, ge=1, le=20, description="Number of quarters to return"),
    db: Session = Depends(get_db),
):
    """
    Get historical market trends for a region.

    Returns quarterly average prices with period-over-period
    percentage changes for the specified region.
    """
    region_upper = region.upper()

    # Query market trends for the region
    trends = db.query(MarketTrend).filter(
        MarketTrend.region.ilike(f"{region_upper}%")
    ).order_by(
        MarketTrend.quarter.desc()
    ).limit(quarters).all()

    if not trends:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No market trend data found for region {region}",
        )

    # Reverse to chronological order
    trends = list(reversed(trends))

    # Build response with price change calculations
    trend_responses = []
    for i, trend in enumerate(trends):
        price_change = None
        if i > 0 and trends[i - 1].avg_price > 0:
            prev_price = trends[i - 1].avg_price
            price_change = round(
                ((trend.avg_price - prev_price) / prev_price) * 100, 2
            )

        trend_responses.append(
            MarketTrendResponse(
                region=trend.region,
                quarter=trend.quarter,
                avg_price=trend.avg_price,
                price_change_pct=price_change,
            )
        )

    return RegionalTrendsResponse(
        region=region_upper,
        trends=trend_responses,
    )
