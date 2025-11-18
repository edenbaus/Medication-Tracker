from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.medication import Medication
from app.models.regimen import Regimen
from app.schemas.regimen import (
    RegimenCreate,
    RegimenUpdate,
    RegimenResponse,
    RegimenList
)

router = APIRouter()


@router.get("/", response_model=RegimenList)
def get_regimens(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all regimens for the current user.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        current_user: Current authenticated user
        db: Database session

    Returns:
        RegimenList: Paginated list of regimens
    """
    query = db.query(Regimen).filter(Regimen.user_id == current_user.id)
    total = query.count()
    regimens = query.offset(skip).limit(limit).all()

    return RegimenList(
        regimens=regimens,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit
    )


@router.get("/{regimen_id}", response_model=RegimenResponse)
def get_regimen(
    regimen_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific regimen by ID.

    Args:
        regimen_id: Regimen ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        RegimenResponse: Regimen details

    Raises:
        HTTPException: If regimen not found or doesn't belong to user
    """
    regimen = db.query(Regimen).filter(
        and_(
            Regimen.id == regimen_id,
            Regimen.user_id == current_user.id
        )
    ).first()

    if not regimen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regimen not found"
        )

    return regimen


@router.post("/", response_model=RegimenResponse, status_code=status.HTTP_201_CREATED)
def create_regimen(
    regimen_data: RegimenCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new regimen.

    Args:
        regimen_data: Regimen data
        current_user: Current authenticated user
        db: Database session

    Returns:
        RegimenResponse: Created regimen

    Raises:
        HTTPException: If any medications don't belong to user
    """
    # Create regimen
    new_regimen = Regimen(
        user_id=current_user.id,
        name=regimen_data.name,
        description=regimen_data.description,
        color=regimen_data.color
    )

    # Validate and add medications
    if regimen_data.medication_ids:
        medications = db.query(Medication).filter(
            and_(
                Medication.id.in_(regimen_data.medication_ids),
                Medication.user_id == current_user.id
            )
        ).all()

        if len(medications) != len(regimen_data.medication_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more medications not found or don't belong to user"
            )

        new_regimen.medications = medications

    db.add(new_regimen)
    db.commit()
    db.refresh(new_regimen)

    return new_regimen


@router.put("/{regimen_id}", response_model=RegimenResponse)
def update_regimen(
    regimen_id: UUID,
    regimen_data: RegimenUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a regimen.

    Args:
        regimen_id: Regimen ID
        regimen_data: Updated regimen data
        current_user: Current authenticated user
        db: Database session

    Returns:
        RegimenResponse: Updated regimen

    Raises:
        HTTPException: If regimen not found or doesn't belong to user
    """
    regimen = db.query(Regimen).filter(
        and_(
            Regimen.id == regimen_id,
            Regimen.user_id == current_user.id
        )
    ).first()

    if not regimen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regimen not found"
        )

    # Update fields
    update_data = regimen_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(regimen, field, value)

    db.commit()
    db.refresh(regimen)

    return regimen


@router.delete("/{regimen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_regimen(
    regimen_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a regimen.

    Note: This only deletes the regimen, not the medications in it.

    Args:
        regimen_id: Regimen ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        None

    Raises:
        HTTPException: If regimen not found or doesn't belong to user
    """
    regimen = db.query(Regimen).filter(
        and_(
            Regimen.id == regimen_id,
            Regimen.user_id == current_user.id
        )
    ).first()

    if not regimen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regimen not found"
        )

    db.delete(regimen)
    db.commit()

    return None


@router.post("/{regimen_id}/medications/{medication_id}", response_model=RegimenResponse)
def add_medication_to_regimen(
    regimen_id: UUID,
    medication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a medication to a regimen.

    Args:
        regimen_id: Regimen ID
        medication_id: Medication ID to add
        current_user: Current authenticated user
        db: Database session

    Returns:
        RegimenResponse: Updated regimen

    Raises:
        HTTPException: If regimen or medication not found or don't belong to user
    """
    regimen = db.query(Regimen).filter(
        and_(
            Regimen.id == regimen_id,
            Regimen.user_id == current_user.id
        )
    ).first()

    if not regimen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regimen not found"
        )

    medication = db.query(Medication).filter(
        and_(
            Medication.id == medication_id,
            Medication.user_id == current_user.id
        )
    ).first()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )

    # Check if already in regimen
    if medication in regimen.medications:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication already in regimen"
        )

    regimen.medications.append(medication)
    db.commit()
    db.refresh(regimen)

    return regimen


@router.delete("/{regimen_id}/medications/{medication_id}", response_model=RegimenResponse)
def remove_medication_from_regimen(
    regimen_id: UUID,
    medication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a medication from a regimen.

    Args:
        regimen_id: Regimen ID
        medication_id: Medication ID to remove
        current_user: Current authenticated user
        db: Database session

    Returns:
        RegimenResponse: Updated regimen

    Raises:
        HTTPException: If regimen or medication not found or don't belong to user
    """
    regimen = db.query(Regimen).filter(
        and_(
            Regimen.id == regimen_id,
            Regimen.user_id == current_user.id
        )
    ).first()

    if not regimen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Regimen not found"
        )

    medication = db.query(Medication).filter(
        and_(
            Medication.id == medication_id,
            Medication.user_id == current_user.id
        )
    ).first()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )

    # Check if in regimen
    if medication not in regimen.medications:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medication not in regimen"
        )

    regimen.medications.remove(medication)
    db.commit()
    db.refresh(regimen)

    return regimen
