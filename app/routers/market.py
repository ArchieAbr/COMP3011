"""
Market Router - CRUD operations for property listings.
Requires API key authentication via X-API-Key header.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..config import verify_api_key
from ..database import get_db
from ..models import Property as PropertyModel
from ..schemas import PropertyCreate, PropertyUpdate, PropertyRead, PropertyList

router = APIRouter(
    prefix="/properties",
    tags=["Properties"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/", response_model=PropertyRead, status_code=status.HTTP_201_CREATED)
def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new property listing.
    """
    db_property = PropertyModel(**property_data.model_dump())
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


@router.get("/", response_model=PropertyList)
def list_properties(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    postcode: Optional[str] = Query(None, description="Filter by postcode prefix"),
    property_type: Optional[str] = Query(None, description="Filter by type"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price"),
    bedrooms: Optional[int] = Query(None, ge=0, description="Number of bedrooms"),
    status: Optional[str] = Query(None, description="Status: for_sale, for_rent, sold, let"),
    db: Session = Depends(get_db),
):
    """
    List properties with optional filtering and pagination.
    """
    query = db.query(PropertyModel)

    # Apply filters
    if postcode:
        query = query.filter(PropertyModel.postcode.ilike(f"{postcode}%"))
    if property_type:
        query = query.filter(PropertyModel.property_type == property_type)
    if min_price is not None:
        query = query.filter(PropertyModel.price >= min_price)
    if max_price is not None:
        query = query.filter(PropertyModel.price <= max_price)
    if bedrooms is not None:
        query = query.filter(PropertyModel.bedrooms == bedrooms)
    if status:
        query = query.filter(PropertyModel.status == status)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * per_page
    properties = query.offset(offset).limit(per_page).all()

    return PropertyList(
        total=total,
        page=page,
        per_page=per_page,
        properties=properties,
    )


@router.get("/{property_id}", response_model=PropertyRead)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a specific property by ID.
    """
    db_property = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()

    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with ID {property_id} not found",
        )

    return db_property


@router.put("/{property_id}", response_model=PropertyRead)
def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
):
    """
    Update a property listing. Only provided fields will be updated.
    """
    db_property = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()

    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with ID {property_id} not found",
        )

    # Update only provided fields
    update_data = property_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_property, field, value)

    db.commit()
    db.refresh(db_property)
    return db_property


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a property listing.
    """
    db_property = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()

    if not db_property:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Property with ID {property_id} not found",
        )

    db.delete(db_property)
    db.commit()
    return None
