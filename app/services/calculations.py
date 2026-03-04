"""
Calculation services for UrbanPulse analytics.
Contains reusable business logic for property and market calculations.
"""
from typing import Optional
from statistics import median, mean


def extract_postcode_sector(postcode: str) -> str:
    """
    Extract the outward code (sector) from a UK postcode.
    
    UK postcodes: "SW1A 1AA" -> "SW1A", "M1 1AA" -> "M1"
    """
    parts = postcode.strip().upper().split()
    return parts[0] if parts else postcode[:4]


def calculate_median(values: list[int | float]) -> float:
    """Calculate median of a list of values."""
    if not values:
        return 0.0
    return median(values)


def calculate_mean(values: list[int | float]) -> float:
    """Calculate mean of a list of values."""
    if not values:
        return 0.0
    return mean(values)


def calculate_cagr(start_value: float, end_value: float, years: int) -> float:
    """
    Calculate Compound Annual Growth Rate.
    
    Returns percentage growth rate.
    """
    if start_value <= 0 or years <= 0:
        return 0.0
    
    cagr = ((end_value / start_value) ** (1 / years) - 1) * 100
    return round(cagr, 2)


def calculate_gross_yield(purchase_price: int, annual_rent: int) -> float:
    """
    Calculate gross rental yield percentage.
    
    Formula: (Annual Rent / Purchase Price) * 100
    """
    if purchase_price <= 0:
        return 0.0
    return round((annual_rent / purchase_price) * 100, 2)


def calculate_net_yield(
    purchase_price: int,
    annual_rent: int,
    annual_costs: int = 0,
) -> float:
    """
    Calculate net rental yield percentage.
    
    Formula: ((Annual Rent - Annual Costs) / Purchase Price) * 100
    """
    if purchase_price <= 0:
        return 0.0
    return round(((annual_rent - annual_costs) / purchase_price) * 100, 2)


def calculate_affordability_ratio(property_price: int, annual_income: int) -> float:
    """
    Calculate price-to-income affordability ratio.
    
    Lower values indicate more affordable areas.
    """
    if annual_income <= 0:
        return float("inf")
    return round(property_price / annual_income, 2)


def get_affordability_band(ratio: float) -> str:
    """
    Classify affordability based on price-to-income ratio.
    
    Bands:
    - affordable: ratio <= 4
    - moderate: 4 < ratio <= 6
    - expensive: 6 < ratio <= 10
    - very_expensive: ratio > 10
    """
    if ratio <= 4:
        return "affordable"
    elif ratio <= 6:
        return "moderate"
    elif ratio <= 10:
        return "expensive"
    else:
        return "very_expensive"


def calculate_safety_score(
    total_crimes: int,
    months: int,
    estimated_population: int = 5000,
) -> float:
    """
    Calculate safety score from crime statistics.
    
    Returns a score from 0-100 (100 = safest).
    """
    if months <= 0 or estimated_population <= 0:
        return 50.0  # Default neutral score
    
    monthly_crimes = total_crimes / months
    crime_rate_per_1000 = (monthly_crimes / estimated_population) * 1000
    
    # UK average is ~80 crimes per 1000 people per year (~6.7 monthly)
    # Scale factor converts crime rate to score
    safety_score = 100 - (crime_rate_per_1000 * 8)
    
    return round(max(0, min(100, safety_score)), 1)


def calculate_mortgage_income_required(
    property_price: int,
    deposit_percentage: float = 10.0,
    income_multiple: float = 4.5,
) -> int:
    """
    Calculate minimum income required for mortgage approval.
    
    Args:
        property_price: Total property price
        deposit_percentage: Deposit as percentage (default 10%)
        income_multiple: Lender's income multiple (default 4.5x)
    
    Returns:
        Minimum annual income required
    """
    mortgage_amount = property_price * (1 - deposit_percentage / 100)
    income_required = mortgage_amount / income_multiple
    return int(income_required)


def determine_trend(
    values: list[int | float],
    threshold: float = 0.1,
) -> str:
    """
    Determine trend from a series of values.
    
    Compares first half to second half.
    Returns: 'improving', 'stable', or 'declining'
    """
    if len(values) < 4:
        return "stable"
    
    mid = len(values) // 2
    first_half_avg = mean(values[:mid])
    second_half_avg = mean(values[mid:])
    
    if first_half_avg == 0:
        return "stable"
    
    change = (second_half_avg - first_half_avg) / first_half_avg
    
    if change > threshold:
        return "declining"  # For crime stats, more is worse
    elif change < -threshold:
        return "improving"
    else:
        return "stable"
