from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.side_effect import SideEffect, SeverityLevel
from app.models.medication import Medication
from app.schemas.side_effect import (
    SideEffectCreate,
    SideEffectUpdate,
    SideEffectResponse,
    SideEffectWithMedication,
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[SideEffectWithMedication])
def get_side_effects(
    medication_id: Optional[UUID] = Query(None, description="Filter by medication ID"),
    third_party_id: Optional[UUID] = Query(None, description="Filter by person (third party ID, or null for self)"),
    severity: Optional[SeverityLevel] = Query(None, description="Filter by severity level"),
    start_date: Optional[datetime] = Query(None, description="Filter side effects from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter side effects until this date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all side effects for the current user with optional filters.

    Args:
        medication_id: Filter by specific medication
        third_party_id: Filter by person (null for self, UUID for third party)
        severity: Filter by severity level (mild, moderate, severe)
        start_date: Filter side effects from this date
        end_date: Filter side effects until this date
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of side effects with medication details
    """
    # Join with Medication to filter by third_party_id
    query = db.query(SideEffect).join(
        Medication, SideEffect.medication_id == Medication.id
    ).filter(SideEffect.user_id == current_user.id)

    # Apply filters
    if medication_id:
        query = query.filter(SideEffect.medication_id == medication_id)
    if third_party_id is not None:
        # Filter by specific third party
        query = query.filter(Medication.third_party_id == third_party_id)
    if severity:
        query = query.filter(SideEffect.severity == severity)
    if start_date:
        query = query.filter(SideEffect.occurred_at >= start_date)
    if end_date:
        query = query.filter(SideEffect.occurred_at <= end_date)

    # Order by most recent first
    query = query.order_by(SideEffect.occurred_at.desc())

    # Apply pagination
    side_effects = query.offset(skip).limit(limit).all()

    # Load medication details for each side effect
    results = []
    for side_effect in side_effects:
        medication = db.query(Medication).filter(Medication.id == side_effect.medication_id).first()
        side_effect_dict = {
            "id": side_effect.id,
            "medication_id": side_effect.medication_id,
            "user_id": side_effect.user_id,
            "severity": side_effect.severity,
            "description": side_effect.description,
            "occurred_at": side_effect.occurred_at,
            "created_at": side_effect.created_at,
            "medication": {
                "id": medication.id,
                "drug_name": medication.drug_name,
            } if medication else None,
        }
        results.append(side_effect_dict)

    return results


@router.post("/", response_model=SideEffectResponse, status_code=status.HTTP_201_CREATED)
def create_side_effect(
    side_effect_data: SideEffectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Report a new side effect.

    Args:
        side_effect_data: Side effect data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created side effect

    Raises:
        HTTPException: If medication not found or doesn't belong to user
    """
    # Verify medication exists and belongs to user
    medication = db.query(Medication).filter(
        Medication.id == side_effect_data.medication_id,
        Medication.user_id == current_user.id,
    ).first()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )

    # Create new side effect
    new_side_effect = SideEffect(
        user_id=current_user.id,
        medication_id=side_effect_data.medication_id,
        severity=side_effect_data.severity,
        description=side_effect_data.description,
        occurred_at=side_effect_data.occurred_at,
    )

    db.add(new_side_effect)
    db.commit()
    db.refresh(new_side_effect)

    return new_side_effect


@router.get("/{side_effect_id}", response_model=SideEffectWithMedication)
def get_side_effect(
    side_effect_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific side effect by ID.

    Args:
        side_effect_id: Side effect ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Side effect details

    Raises:
        HTTPException: If side effect not found or doesn't belong to user
    """
    side_effect = db.query(SideEffect).filter(
        SideEffect.id == side_effect_id,
        SideEffect.user_id == current_user.id,
    ).first()

    if not side_effect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Side effect not found",
        )

    # Load medication details
    medication = db.query(Medication).filter(Medication.id == side_effect.medication_id).first()

    return {
        "id": side_effect.id,
        "medication_id": side_effect.medication_id,
        "user_id": side_effect.user_id,
        "severity": side_effect.severity,
        "description": side_effect.description,
        "occurred_at": side_effect.occurred_at,
        "created_at": side_effect.created_at,
        "medication": {
            "id": medication.id,
            "drug_name": medication.drug_name,
        } if medication else None,
    }


@router.put("/{side_effect_id}", response_model=SideEffectResponse)
def update_side_effect(
    side_effect_id: UUID,
    side_effect_data: SideEffectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a side effect report.

    Args:
        side_effect_id: Side effect ID
        side_effect_data: Updated side effect data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated side effect

    Raises:
        HTTPException: If side effect not found or doesn't belong to user
    """
    side_effect = db.query(SideEffect).filter(
        SideEffect.id == side_effect_id,
        SideEffect.user_id == current_user.id,
    ).first()

    if not side_effect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Side effect not found",
        )

    # Update fields if provided
    update_data = side_effect_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(side_effect, field, value)

    db.commit()
    db.refresh(side_effect)

    return side_effect


@router.delete("/{side_effect_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_side_effect(
    side_effect_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a side effect report.

    Args:
        side_effect_id: Side effect ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If side effect not found or doesn't belong to user
    """
    side_effect = db.query(SideEffect).filter(
        SideEffect.id == side_effect_id,
        SideEffect.user_id == current_user.id,
    ).first()

    if not side_effect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Side effect not found",
        )

    db.delete(side_effect)
    db.commit()

    return None
