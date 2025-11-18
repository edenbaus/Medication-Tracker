"""Dashboard summary schemas."""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class RecentActivity(BaseModel):
    """Recent activity item."""
    id: UUID
    activity_type: str  # "log", "side_effect", "symptom", "medication_added"
    timestamp: datetime
    description: str
    medication_name: Optional[str] = None
    severity: Optional[str] = None
    person_id: Optional[UUID] = None
    person_name: str = "Me"

    class Config:
        from_attributes = True


class MedicationSummary(BaseModel):
    """Quick medication summary."""
    medication_id: UUID
    medication_name: str
    last_logged: Optional[datetime] = None
    days_since_last_log: Optional[int] = None
    total_logs: int = 0
    is_active: bool = True
    person_id: Optional[UUID] = None
    person_name: str = "Me"


class RefillAlert(BaseModel):
    """Medication refill alert."""
    medication_id: UUID
    medication_name: str
    refill_date: Optional[date] = None
    days_until_refill: int = 0
    refills_remaining: int = 0
    date_filled: Optional[date] = None
    days_supply: Optional[int] = None
    person_id: Optional[UUID] = None
    person_name: str = "Me"

    class Config:
        from_attributes = True


class PersonStats(BaseModel):
    """Statistics for a person."""
    person_id: Optional[UUID] = None
    person_name: str = "Me"
    active_medications: int = 0
    total_logs_7days: int = 0
    side_effects_7days: int = 0
    symptoms_tracked_7days: int = 0


class DashboardSummary(BaseModel):
    """Complete dashboard summary."""
    user_name: str
    total_active_medications: int = 0
    total_logs_today: int = 0
    total_logs_7days: int = 0
    total_side_effects_7days: int = 0
    total_symptoms_tracked_7days: int = 0

    # Per-person breakdown
    people_stats: List[PersonStats] = []

    # Recent activity (last 10 events)
    recent_activity: List[RecentActivity] = []

    # Medications needing attention (not logged recently)
    medications_needing_attention: List[MedicationSummary] = []

    # Medications due for refill
    refill_alerts: List[RefillAlert] = []

    class Config:
        from_attributes = True
