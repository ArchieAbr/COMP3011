"""
Living Router - Analytics endpoints for relocators/renters.
Provides safety scoring based on crime statistics.
"""
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CrimeStat
from ..schemas import SafetyScoreResponse

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
