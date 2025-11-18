from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.database import get_db
from app.api.deps import get_current_user
from app.models import User, Medication, Tag
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse, MedicationList

router = APIRouter()


@router.get("/", response_model=MedicationList)
def get_medications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active: Optional[bool] = None,
    prescription_type: Optional[str] = None,
    tag_ids: Optional[List[UUID]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all medications for the current user with optional filters.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **active**: Filter by active status
    - **prescription_type**: Filter by prescription type (long_term, short_term, otc)
    - **tag_ids**: Filter by tag IDs (returns medications with ANY of the specified tags)
    """
    query = db.query(Medication).filter(Medication.user_id == current_user.id)

    # Apply filters
    if active is not None:
        query = query.filter(Medication.active == active)

    if prescription_type:
        query = query.filter(Medication.prescription_type == prescription_type)

    if tag_ids:
        # Filter medications that have at least one of the specified tags
        query = query.join(Medication.tags).filter(Tag.id.in_(tag_ids)).distinct()

    total = query.count()
    medications = query.order_by(Medication.created_at.desc()).offset(skip).limit(limit).all()

    return MedicationList(
        medications=medications,
        total=total,
        page=(skip // limit) + 1 if limit > 0 else 1,
        page_size=limit
    )


@router.post("/", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
def create_medication(
    medication_in: MedicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new medication for the current user.

    Can optionally assign tags during creation using tag_ids.
    """
    # Validate tags belong to the current user
    if medication_in.tag_ids:
        tags = db.query(Tag).filter(
            and_(
                Tag.id.in_(medication_in.tag_ids),
                Tag.user_id == current_user.id
            )
        ).all()

        if len(tags) != len(medication_in.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tags not found or do not belong to you"
            )
    else:
        tags = []

    # Create medication
    medication_data = medication_in.model_dump(exclude={"tag_ids"})
    medication = Medication(**medication_data, user_id=current_user.id)

    # Assign tags
    medication.tags = tags

    db.add(medication)
    db.commit()
    db.refresh(medication)

    return medication


@router.get("/{medication_id}", response_model=MedicationResponse)
def get_medication(
    medication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific medication by ID.

    Only returns the medication if it belongs to the current user.
    """
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

    return medication


@router.put("/{medication_id}", response_model=MedicationResponse)
def update_medication(
    medication_id: UUID,
    medication_in: MedicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing medication.

    Only allows updating medications that belong to the current user.
    """
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

    # Update medication fields
    update_data = medication_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(medication, field, value)

    db.commit()
    db.refresh(medication)

    return medication


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication(
    medication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a medication by setting active=False.

    Only allows deleting medications that belong to the current user.
    """
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

    medication.active = False
    db.commit()

    return None


@router.post("/{medication_id}/tags/{tag_id}", response_model=MedicationResponse)
def add_tag_to_medication(
    medication_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a tag to a medication.

    Both the medication and tag must belong to the current user.
    """
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

    tag = db.query(Tag).filter(
        and_(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # Check if tag is already assigned
    if tag in medication.tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag is already assigned to this medication"
        )

    medication.tags.append(tag)
    db.commit()
    db.refresh(medication)

    return medication


@router.delete("/{medication_id}/tags/{tag_id}", response_model=MedicationResponse)
def remove_tag_from_medication(
    medication_id: UUID,
    tag_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove a tag from a medication.

    Both the medication and tag must belong to the current user.
    """
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

    tag = db.query(Tag).filter(
        and_(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    # Check if tag is assigned
    if tag not in medication.tags:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag is not assigned to this medication"
        )

    medication.tags.remove(tag)
    db.commit()
    db.refresh(medication)

    return medication
