from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.symptom import SymptomTracking
from app.models.medication import Medication
from app.schemas.symptom import (
    SymptomCreate,
    SymptomUpdate,
    SymptomResponse,
    SymptomWithMedication,
    SymptomTrendData,
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[SymptomWithMedication])
def get_symptoms(
    medication_id: Optional[UUID] = Query(None, description="Filter by medication ID"),
    third_party_id: Optional[UUID] = Query(None, description="Filter by person (third party ID, or null for self)"),
    symptom_name: Optional[str] = Query(None, description="Filter by symptom name"),
    start_date: Optional[datetime] = Query(None, description="Filter symptoms from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter symptoms until this date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all symptom tracking entries for the current user with optional filters.

    Args:
        medication_id: Filter by specific medication
        third_party_id: Filter by person (null for self, UUID for third party)
        symptom_name: Filter by symptom name (case-insensitive partial match)
        start_date: Filter symptoms from this date
        end_date: Filter symptoms until this date
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of symptom tracking entries with medication details
    """
    # Join with Medication to filter by third_party_id
    query = db.query(SymptomTracking).join(
        Medication, SymptomTracking.medication_id == Medication.id
    ).filter(SymptomTracking.user_id == current_user.id)

    # Apply filters
    if medication_id:
        query = query.filter(SymptomTracking.medication_id == medication_id)
    if third_party_id is not None:
        # Filter by specific third party
        query = query.filter(Medication.third_party_id == third_party_id)
    if symptom_name:
        query = query.filter(SymptomTracking.symptom_name.ilike(f"%{symptom_name}%"))
    if start_date:
        query = query.filter(SymptomTracking.recorded_at >= start_date)
    if end_date:
        query = query.filter(SymptomTracking.recorded_at <= end_date)

    # Order by most recent first
    query = query.order_by(SymptomTracking.recorded_at.desc())

    # Apply pagination
    symptoms = query.offset(skip).limit(limit).all()

    # Load medication details for each symptom
    results = []
    for symptom in symptoms:
        medication = db.query(Medication).filter(Medication.id == symptom.medication_id).first()
        symptom_dict = {
            "id": symptom.id,
            "medication_id": symptom.medication_id,
            "user_id": symptom.user_id,
            "symptom_name": symptom.symptom_name,
            "improvement_level": symptom.improvement_level,
            "notes": symptom.notes,
            "recorded_at": symptom.recorded_at,
            "created_at": symptom.created_at,
            "medication": {
                "id": medication.id,
                "drug_name": medication.drug_name,
            } if medication else None,
        }
        results.append(symptom_dict)

    return results


@router.post("/", response_model=SymptomResponse, status_code=status.HTTP_201_CREATED)
def create_symptom(
    symptom_data: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new symptom tracking entry.

    Args:
        symptom_data: Symptom tracking data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Created symptom tracking entry

    Raises:
        HTTPException: If medication not found or doesn't belong to user
    """
    # Verify medication exists and belongs to user
    medication = db.query(Medication).filter(
        Medication.id == symptom_data.medication_id,
        Medication.user_id == current_user.id,
    ).first()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )

    # Create new symptom tracking entry
    new_symptom = SymptomTracking(
        user_id=current_user.id,
        medication_id=symptom_data.medication_id,
        symptom_name=symptom_data.symptom_name,
        improvement_level=symptom_data.improvement_level,
        notes=symptom_data.notes,
        recorded_at=symptom_data.recorded_at,
    )

    db.add(new_symptom)
    db.commit()
    db.refresh(new_symptom)

    return new_symptom


@router.get("/trends", response_model=List[SymptomTrendData])
def get_symptom_trends(
    medication_id: Optional[UUID] = Query(None, description="Filter by medication ID"),
    symptom_name: Optional[str] = Query(None, description="Filter by symptom name"),
    start_date: Optional[datetime] = Query(None, description="Filter trends from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter trends until this date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get symptom improvement trends and analytics.

    Analyzes symptom tracking data to show trends over time, including:
    - Average improvement level
    - Number of data points
    - Trend direction (improving, stable, worsening)

    Args:
        medication_id: Filter by specific medication
        symptom_name: Filter by symptom name
        start_date: Filter trends from this date
        end_date: Filter trends until this date
        db: Database session
        current_user: Current authenticated user

    Returns:
        List of symptom trends with analytics
    """
    query = db.query(SymptomTracking).filter(SymptomTracking.user_id == current_user.id)

    # Apply filters
    if medication_id:
        query = query.filter(SymptomTracking.medication_id == medication_id)
    if symptom_name:
        query = query.filter(SymptomTracking.symptom_name.ilike(f"%{symptom_name}%"))
    if start_date:
        query = query.filter(SymptomTracking.recorded_at >= start_date)
    if end_date:
        query = query.filter(SymptomTracking.recorded_at <= end_date)

    # Get all symptoms
    symptoms = query.order_by(SymptomTracking.recorded_at.asc()).all()

    # Group by medication and symptom name
    symptom_groups = {}
    for symptom in symptoms:
        key = (symptom.medication_id, symptom.symptom_name)
        if key not in symptom_groups:
            symptom_groups[key] = []
        symptom_groups[key].append(symptom)

    # Calculate trends for each group
    trends = []
    for (med_id, symp_name), entries in symptom_groups.items():
        if len(entries) < 2:
            trend_direction = "insufficient_data"
        else:
            # Calculate trend by comparing first half vs second half
            mid_point = len(entries) // 2
            first_half_avg = sum(e.improvement_level for e in entries[:mid_point]) / mid_point
            second_half_avg = sum(e.improvement_level for e in entries[mid_point:]) / (len(entries) - mid_point)

            if second_half_avg > first_half_avg + 1:
                trend_direction = "improving"
            elif second_half_avg < first_half_avg - 1:
                trend_direction = "worsening"
            else:
                trend_direction = "stable"

        # Get medication details
        medication = db.query(Medication).filter(Medication.id == med_id).first()

        avg_improvement = sum(e.improvement_level for e in entries) / len(entries)

        trends.append({
            "symptom_name": symp_name,
            "medication_id": med_id,
            "medication_name": medication.drug_name if medication else "Unknown",
            "average_improvement": round(avg_improvement, 2),
            "data_points": len(entries),
            "trend": trend_direction,
            "entries": [
                {
                    "recorded_at": e.recorded_at.isoformat(),
                    "improvement_level": e.improvement_level,
                    "notes": e.notes,
                }
                for e in entries
            ],
        })

    return trends


@router.get("/{symptom_id}", response_model=SymptomWithMedication)
def get_symptom(
    symptom_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific symptom tracking entry by ID.

    Args:
        symptom_id: Symptom tracking ID
        db: Database session
        current_user: Current authenticated user

    Returns:
        Symptom tracking details

    Raises:
        HTTPException: If symptom not found or doesn't belong to user
    """
    symptom = db.query(SymptomTracking).filter(
        SymptomTracking.id == symptom_id,
        SymptomTracking.user_id == current_user.id,
    ).first()

    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom tracking entry not found",
        )

    # Load medication details
    medication = db.query(Medication).filter(Medication.id == symptom.medication_id).first()

    return {
        "id": symptom.id,
        "medication_id": symptom.medication_id,
        "user_id": symptom.user_id,
        "symptom_name": symptom.symptom_name,
        "improvement_level": symptom.improvement_level,
        "notes": symptom.notes,
        "recorded_at": symptom.recorded_at,
        "created_at": symptom.created_at,
        "medication": {
            "id": medication.id,
            "drug_name": medication.drug_name,
        } if medication else None,
    }


@router.put("/{symptom_id}", response_model=SymptomResponse)
def update_symptom(
    symptom_id: UUID,
    symptom_data: SymptomUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a symptom tracking entry.

    Args:
        symptom_id: Symptom tracking ID
        symptom_data: Updated symptom data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated symptom tracking entry

    Raises:
        HTTPException: If symptom not found or doesn't belong to user
    """
    symptom = db.query(SymptomTracking).filter(
        SymptomTracking.id == symptom_id,
        SymptomTracking.user_id == current_user.id,
    ).first()

    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom tracking entry not found",
        )

    # Update fields if provided
    update_data = symptom_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(symptom, field, value)

    db.commit()
    db.refresh(symptom)

    return symptom


@router.delete("/{symptom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_symptom(
    symptom_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a symptom tracking entry.

    Args:
        symptom_id: Symptom tracking ID
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If symptom not found or doesn't belong to user
    """
    symptom = db.query(SymptomTracking).filter(
        SymptomTracking.id == symptom_id,
        SymptomTracking.user_id == current_user.id,
    ).first()

    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom tracking entry not found",
        )

    db.delete(symptom)
    db.commit()

    return None
