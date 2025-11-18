from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class JourneyEvent(BaseModel):
    """Base schema for a journey event."""
    id: UUID
    event_type: str  # "medication_start", "log", "side_effect", "symptom"
    timestamp: datetime
    medication_id: Optional[UUID] = None
    medication_name: Optional[str] = None
    description: str
    severity: Optional[str] = None  # For side effects
    improvement_level: Optional[int] = None  # For symptoms
    person_id: Optional[UUID] = None
    person_name: str = "Me"


class MedicationJourney(BaseModel):
    """Schema for a medication's complete journey with associated events."""
    medication_id: UUID
    medication_name: str
    start_date: datetime
    end_date: Optional[datetime] = None
    person_id: Optional[UUID] = None
    person_name: str = "Me"

    # Associated events
    logs_count: int = 0
    side_effects: List[dict] = []
    symptoms_treated: List[dict] = []

    # Visual indicators
    color: str = "#007bff"
    is_active: bool = True


class SymptomMedicationCorrelation(BaseModel):
    """Schema showing which symptoms are treated by which medications."""
    symptom_name: str
    medications: List[dict]  # List of medication names with improvement data
    average_improvement: float
    trend: str  # "improving", "stable", "worsening"


class MedicationSideEffectCorrelation(BaseModel):
    """Schema showing side effects associated with each medication."""
    medication_id: UUID
    medication_name: str
    person_name: str
    side_effects: List[dict]  # List of side effects with severity
    side_effect_count: int
    severity_distribution: dict  # Count of mild, moderate, severe


class JourneyTimeline(BaseModel):
    """Complete journey timeline visualization data."""
    person_id: Optional[UUID] = None
    person_name: str = "Me"
    period_start: datetime
    period_end: datetime

    # Timeline events (chronological)
    events: List[JourneyEvent] = []

    # Medication journeys
    medications: List[MedicationJourney] = []

    # Correlations
    symptom_medication_correlations: List[SymptomMedicationCorrelation] = []
    medication_side_effect_correlations: List[MedicationSideEffectCorrelation] = []

    # Summary statistics
    total_medications: int = 0
    total_logs: int = 0
    total_side_effects: int = 0
    total_symptoms_tracked: int = 0
