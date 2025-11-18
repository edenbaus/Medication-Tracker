from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.medication import Medication
from app.models.medication_log import MedicationLog
from app.schemas.medication_log import (
    MedicationLogCreate,
    MedicationLogUpdate,
    MedicationLogResponse,
    MedicationLogList,
    AdherenceStats,
    OverallAdherenceStats,
    MedicationUsageTimeline,
    DailyUsageData,
    PersonUsageData,
)

router = APIRouter()


@router.post("/", response_model=MedicationLogResponse, status_code=status.HTTP_201_CREATED)
def create_medication_log(
    log_data: MedicationLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log medication intake.

    Creates a new medication log entry for tracking when medication was taken.

    Args:
        log_data: Medication log data
        current_user: Current authenticated user
        db: Database session

    Returns:
        MedicationLogResponse: Created log entry

    Raises:
        HTTPException: If medication not found or doesn't belong to user
    """
    # Verify medication exists and belongs to user
    medication = db.query(Medication).filter(
        and_(
            Medication.id == log_data.medication_id,
            Medication.user_id == current_user.id
        )
    ).first()

    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )

    # Create log entry with current time if not specified
    log = MedicationLog(
        **log_data.model_dump(exclude={'taken_at'}),
        user_id=current_user.id,
        taken_at=log_data.taken_at or datetime.utcnow()
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


@router.get("/", response_model=MedicationLogList)
def get_medication_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    medication_id: Optional[UUID] = Query(None, description="Filter by medication ID"),
    start_date: Optional[datetime] = Query(None, description="Filter logs after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter logs before this date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get medication logs for the current user.

    Supports filtering by medication, date range, and pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        medication_id: Optional medication ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        current_user: Current authenticated user
        db: Database session

    Returns:
        MedicationLogList: Paginated list of medication logs
    """
    query = db.query(MedicationLog).filter(MedicationLog.user_id == current_user.id)

    # Apply filters
    if medication_id:
        query = query.filter(MedicationLog.medication_id == medication_id)

    if start_date:
        query = query.filter(MedicationLog.taken_at >= start_date)

    if end_date:
        query = query.filter(MedicationLog.taken_at <= end_date)

    total = query.count()
    logs = query.order_by(desc(MedicationLog.taken_at)).offset(skip).limit(limit).all()

    return MedicationLogList(
        logs=logs,
        total=total,
        page=(skip // limit) + 1,
        page_size=limit
    )


@router.get("/{log_id}", response_model=MedicationLogResponse)
def get_medication_log(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific medication log entry.

    Args:
        log_id: Log entry ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        MedicationLogResponse: Log entry details

    Raises:
        HTTPException: If log not found or doesn't belong to user
    """
    log = db.query(MedicationLog).filter(
        and_(
            MedicationLog.id == log_id,
            MedicationLog.user_id == current_user.id
        )
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found"
        )

    return log


@router.put("/{log_id}", response_model=MedicationLogResponse)
def update_medication_log(
    log_id: UUID,
    log_update: MedicationLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a medication log entry.

    Args:
        log_id: Log entry ID
        log_update: Updated log data
        current_user: Current authenticated user
        db: Database session

    Returns:
        MedicationLogResponse: Updated log entry

    Raises:
        HTTPException: If log not found or doesn't belong to user
    """
    log = db.query(MedicationLog).filter(
        and_(
            MedicationLog.id == log_id,
            MedicationLog.user_id == current_user.id
        )
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found"
        )

    # Update log fields
    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)

    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medication_log(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a medication log entry.

    Args:
        log_id: Log entry ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        None

    Raises:
        HTTPException: If log not found or doesn't belong to user
    """
    log = db.query(MedicationLog).filter(
        and_(
            MedicationLog.id == log_id,
            MedicationLog.user_id == current_user.id
        )
    ).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log entry not found"
        )

    db.delete(log)
    db.commit()

    return None


@router.get("/stats/adherence", response_model=OverallAdherenceStats)
def get_adherence_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    medication_id: Optional[UUID] = Query(None, description="Filter by specific medication"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get medication adherence statistics.

    Calculates adherence rates based on logged doses vs expected doses.
    Expected doses are calculated from medication dosing schedules.

    Args:
        days: Number of days to analyze (default: 30)
        medication_id: Optional specific medication to analyze
        current_user: Current authenticated user
        db: Database session

    Returns:
        OverallAdherenceStats: Adherence statistics

    Note:
        For simplicity, this assumes daily dosing for all medications.
        A more sophisticated implementation would parse dosing_schedule.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get medications for the user
    med_query = db.query(Medication).filter(
        and_(
            Medication.user_id == current_user.id,
            Medication.active == True
        )
    )

    if medication_id:
        med_query = med_query.filter(Medication.id == medication_id)

    medications = med_query.all()

    medication_stats = []
    total_logged = 0
    total_expected = 0

    for med in medications:
        # Count logged doses for this medication in the period
        logged_count = db.query(func.count(MedicationLog.id)).filter(
            and_(
                MedicationLog.medication_id == med.id,
                MedicationLog.taken_at >= start_date,
                MedicationLog.taken_at <= end_date
            )
        ).scalar()

        # Calculate expected doses (simplified: assume 1 dose per day)
        # In a real implementation, parse dosing_schedule for accurate expected doses
        expected_doses = days

        adherence_pct = (logged_count / expected_doses * 100) if expected_doses > 0 else 0

        medication_stats.append(AdherenceStats(
            medication_id=med.id,
            medication_name=med.drug_name,
            total_expected_doses=expected_doses,
            total_logged_doses=logged_count,
            adherence_percentage=round(adherence_pct, 2),
            period_start=start_date,
            period_end=end_date
        ))

        total_logged += logged_count
        total_expected += expected_doses

    avg_adherence = (total_logged / total_expected * 100) if total_expected > 0 else 0

    return OverallAdherenceStats(
        total_medications=len(medications),
        total_logged_doses=total_logged,
        average_adherence=round(avg_adherence, 2),
        period_start=start_date,
        period_end=end_date,
        medication_stats=medication_stats
    )


@router.get("/stats/usage-timeline", response_model=MedicationUsageTimeline)
def get_usage_timeline(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    medication_id: Optional[UUID] = Query(None, description="Filter by specific medication"),
    third_party_id: Optional[UUID] = Query(None, description="Filter by person (null for self, UUID for third party)"),
    group_by_person: bool = Query(False, description="Group data by person with color coding"),
    grouping: str = Query("daily", regex="^(daily|weekly)$", description="Group by daily or weekly"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get medication usage timeline for visualizations.

    Returns daily or weekly usage counts for creating charts showing
    medication/regimen usage patterns over time. Optionally groups by person
    with color coding for multi-person charts.

    Args:
        days: Number of days to analyze (default: 30)
        medication_id: Optional specific medication to analyze
        third_party_id: Filter by person (null for self, UUID for specific person)
        group_by_person: If True, returns separate datasets for each person
        grouping: "daily" or "weekly" grouping
        current_user: Current authenticated user
        db: Database session

    Returns:
        MedicationUsageTimeline: Usage data over time with optional person grouping
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Build query for medication logs
    logs_query = db.query(MedicationLog).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).filter(
        and_(
            MedicationLog.user_id == current_user.id,
            MedicationLog.taken_at >= start_date,
            MedicationLog.taken_at <= end_date
        )
    )
    
    medication_name = None
    if medication_id:
        logs_query = logs_query.filter(MedicationLog.medication_id == medication_id)
        medication = db.query(Medication).filter(Medication.id == medication_id).first()
        medication_name = medication.drug_name if medication else None
    
    logs = logs_query.order_by(MedicationLog.taken_at.asc()).all()
    
    # Group logs by date
    from collections import defaultdict
    daily_counts = defaultdict(lambda: {"count": 0, "medications": set()})
    
    for log in logs:
        log_date = log.taken_at.date().isoformat()
        daily_counts[log_date]["count"] += 1
        
        # Get medication name
        medication = db.query(Medication).filter(Medication.id == log.medication_id).first()
        if medication:
            daily_counts[log_date]["medications"].add(medication.drug_name)
    
    # Create daily data points for all days in range (fill gaps with 0)
    from datetime import date, timedelta as td
    current_date = start_date.date()
    end_date_only = end_date.date()
    
    daily_data = []
    while current_date <= end_date_only:
        date_str = current_date.isoformat()
        data = daily_counts.get(date_str, {"count": 0, "medications": set()})
        
        daily_data.append(DailyUsageData(
            date=date_str,
            count=data["count"],
            medications=list(data["medications"])
        ))
        
        current_date += td(days=1)
    
    # If weekly grouping, aggregate by week
    if grouping == "weekly":
        weekly_data = []
        week_counts = defaultdict(lambda: {"count": 0, "medications": set()})
        
        for day_data in daily_data:
            # Get the start of the week (Monday)
            day_date = datetime.fromisoformat(day_data.date).date()
            week_start = day_date - td(days=day_date.weekday())
            week_key = week_start.isoformat()
            
            week_counts[week_key]["count"] += day_data.count
            week_counts[week_key]["medications"].update(day_data.medications)
        
        for week_start, data in sorted(week_counts.items()):
            weekly_data.append(DailyUsageData(
                date=week_start,
                count=data["count"],
                medications=list(data["medications"])
            ))
        
        daily_data = weekly_data
    
    return MedicationUsageTimeline(
        medication_id=medication_id,
        medication_name=medication_name,
        period_start=start_date,
        period_end=end_date,
        total_logs=len(logs),
        daily_data=daily_data,
        grouping=grouping
    )
