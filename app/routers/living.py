"""
Living Router - Analytics endpoints for relocators/renters.
Provides safety scoring based on crime statistics.
"""
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CrimeStat, Property as PropertyModel
from ..schemas import SafetyScoreResponse, AffordabilityResponse

router = APIRouter(
    prefix="/living",
    tags=["Living Analytics"],
)


def extract_postcode_sector(postcode: str) -> str:
    """Extract the outward code (sector) from a UK postcode."""
    parts = postcode.strip().upper().split()
    return parts[0] if parts else postcode[:4]


def calculate_safety_score(crime_count: int, months: int) -> int:
    """
    Calculate safety score (0-100) based on crime count.
    
    Uses monthly crime rate benchmarks:
    - 0-5 crimes/month = 100
    - 50+ crimes/month = 0
    """
    if months == 0:
        return 50  # No data, neutral score
    
    monthly_rate = crime_count / months
    
    # Linear scale: 0 crimes = 100, 50+ crimes = 0
    score = max(0, min(100, int(100 - (monthly_rate * 2))))
    return score


def get_safety_rating(score: int) -> str:
    """Convert numeric score to rating label."""
    if score >= 80:
        return "very_safe"
    elif score >= 60:
        return "safe"
    elif score >= 40:
        return "moderate"
    elif score >= 20:
        return "caution"
    else:
        return "high_risk"


@router.get("/safety-score/{postcode}", response_model=SafetyScoreResponse)
def get_safety_score(
    postcode: str,
    db: Session = Depends(get_db),
):
    """
    Get safety score for a specific postcode.
    
    Analyses crime statistics for the postcode sector to calculate
    a safety score from 0-100 (higher = safer).
    """
    sector = extract_postcode_sector(postcode)
    
    # Get crime stats for this postcode sector
    crime_stats = db.query(CrimeStat).filter(
        CrimeStat.postcode_sector.ilike(f"{sector}%")
    ).all()
    
    if not crime_stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No crime data found for postcode {postcode}",
        )
    
    # Calculate totals
    total_crimes = sum(stat.crime_count for stat in crime_stats)
    
    # Get unique months for data coverage
    unique_months = len(set(stat.month for stat in crime_stats))
    data_months = min(unique_months, 6)  # Cap at 6 for scoring
    
    # Get top crime categories
    category_counts = Counter()
    for stat in crime_stats:
        category_counts[stat.category] += stat.crime_count
    
    top_categories = [cat for cat, _ in category_counts.most_common(3)]
    
    # Calculate score
    safety_score = calculate_safety_score(total_crimes, data_months)
    rating = get_safety_rating(safety_score)
    
    return SafetyScoreResponse(
        postcode=postcode.upper(),
        safety_score=safety_score,
        crime_count_6m=total_crimes,
        top_crime_categories=top_categories,
        rating=rating,
        data_months=data_months,
    )


def calculate_affordability_index(price_to_rent_ratio: float) -> int:
    """
    Calculate affordability index (0-100) based on price-to-rent ratio.
    
    Lower ratio = more affordable to buy vs rent.
    UK average is ~15-20. Below 15 = affordable, above 25 = expensive.
    """
    # Scale: ratio 10 = 100 (very affordable), ratio 30+ = 0 (very expensive)
    index = max(0, min(100, int((30 - price_to_rent_ratio) * 5)))
    return index


def get_affordability_rating(index: int) -> str:
    """Convert affordability index to rating label."""
    if index >= 80:
        return "very_affordable"
    elif index >= 60:
        return "affordable"
    elif index >= 40:
        return "moderate"
    elif index >= 20:
        return "expensive"
    else:
        return "very_expensive"


@router.get("/affordability/{postcode}", response_model=AffordabilityResponse)
def get_affordability(
    postcode: str,
    db: Session = Depends(get_db),
):
    """
    Get affordability analysis for a specific postcode.
    
    Calculates price-to-rent ratio and affordability index
    based on local property data.
    """
    sector = extract_postcode_sector(postcode)
    
    # Get properties with both price and rent data
    properties = db.query(PropertyModel).filter(
        PropertyModel.postcode.ilike(f"{sector}%"),
        PropertyModel.price > 0,
        PropertyModel.rent_pcm > 0,
    ).all()
    
    if not properties:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No property data found for postcode {postcode}",
        )
    
    # Calculate averages
    avg_price = int(sum(p.price for p in properties) / len(properties))
    avg_rent = int(sum(p.rent_pcm for p in properties) / len(properties))
    
    # Price-to-rent ratio (price / annual rent)
    annual_rent = avg_rent * 12
    price_to_rent = round(avg_price / annual_rent, 2) if annual_rent > 0 else 0
    
    # Calculate affordability index
    affordability_index = calculate_affordability_index(price_to_rent)
    rating = get_affordability_rating(affordability_index)
    
    return AffordabilityResponse(
        postcode=postcode.upper(),
        avg_property_price=avg_price,
        avg_monthly_rent=avg_rent,
        price_to_rent_ratio=price_to_rent,
        affordability_index=affordability_index,
        rating=rating,
        properties_analysed=len(properties),
    )
