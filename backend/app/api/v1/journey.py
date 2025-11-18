from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID
from collections import defaultdict

from app.database import get_db
from app.models.user import User
from app.models.medication import Medication
from app.models.medication_log import MedicationLog
from app.models.side_effect import SideEffect
from app.models.symptom import SymptomTracking
from app.models.third_party import ThirdParty
from app.schemas.journey import (
    JourneyTimeline,
    JourneyEvent,
    MedicationJourney,
    SymptomMedicationCorrelation,
    MedicationSideEffectCorrelation,
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/timeline", response_model=JourneyTimeline)
def get_journey_timeline(
    days: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
    third_party_id: Optional[UUID] = Query(None, description="Filter by person (null for self)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get comprehensive journey timeline showing symptoms, medications, and side effects.

    This endpoint provides a holistic view of a person's medication journey:
    - Which symptoms led to which medications
    - How symptoms improved with treatment
    - Which side effects occurred with each medication
    - Complete chronological timeline of all events

    Args:
        days: Number of days to analyze (default: 90)
        third_party_id: Filter by person (null for self)
        db: Database session
        current_user: Current authenticated user

    Returns:
        JourneyTimeline: Complete journey data with correlations
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get person name
    person_name = "Me"
    if third_party_id:
        third_party = db.query(ThirdParty).filter(ThirdParty.id == third_party_id).first()
        if third_party:
            person_name = third_party.name

    # Get all medications for this person in the time period
    meds_query = db.query(Medication).filter(
        Medication.user_id == current_user.id,
        Medication.start_date <= end_date
    )

    if third_party_id is not None:
        meds_query = meds_query.filter(Medication.third_party_id == third_party_id)
    else:
        meds_query = meds_query.filter(Medication.third_party_id.is_(None))

    medications = meds_query.all()

    # Color palette for medications
    colors = [
        "#007bff", "#28a745", "#dc3545", "#ffc107",
        "#17a2b8", "#6f42c1", "#fd7e14", "#20c997"
    ]

    # Build timeline events and medication journeys
    events = []
    medication_journeys = []

    for idx, med in enumerate(medications):
        med_color = colors[idx % len(colors)]

        # Medication start event
        events.append(JourneyEvent(
            id=med.id,
            event_type="medication_start",
            timestamp=med.start_date,
            medication_id=med.id,
            medication_name=med.drug_name,
            description=f"Started {med.drug_name} ({med.standard_dose})",
            person_id=third_party_id,
            person_name=person_name
        ))

        # Get logs for this medication
        logs = db.query(MedicationLog).filter(
            and_(
                MedicationLog.medication_id == med.id,
                MedicationLog.taken_at >= start_date,
                MedicationLog.taken_at <= end_date
            )
        ).all()

        # Add log events (sample some to avoid clutter)
        for log in logs[:50]:  # Limit to 50 most recent
            events.append(JourneyEvent(
                id=log.id,
                event_type="log",
                timestamp=log.taken_at,
                medication_id=med.id,
                medication_name=med.drug_name,
                description=f"Took {med.drug_name} ({log.dose_taken})",
                person_id=third_party_id,
                person_name=person_name
            ))

        # Get side effects for this medication
        side_effects = db.query(SideEffect).filter(
            and_(
                SideEffect.medication_id == med.id,
                SideEffect.occurred_at >= start_date,
                SideEffect.occurred_at <= end_date
            )
        ).all()

        side_effects_data = []
        for se in side_effects:
            events.append(JourneyEvent(
                id=se.id,
                event_type="side_effect",
                timestamp=se.occurred_at,
                medication_id=med.id,
                medication_name=med.drug_name,
                description=f"Side effect: {se.description[:50]}...",
                severity=se.severity.value,
                person_id=third_party_id,
                person_name=person_name
            ))
            side_effects_data.append({
                "description": se.description,
                "severity": se.severity.value,
                "occurred_at": se.occurred_at.isoformat()
            })

        # Get symptoms for this medication
        symptoms = db.query(SymptomTracking).filter(
            and_(
                SymptomTracking.medication_id == med.id,
                SymptomTracking.recorded_at >= start_date,
                SymptomTracking.recorded_at <= end_date
            )
        ).all()

        symptoms_data = []
        for symptom in symptoms:
            events.append(JourneyEvent(
                id=symptom.id,
                event_type="symptom",
                timestamp=symptom.recorded_at,
                medication_id=med.id,
                medication_name=med.drug_name,
                description=f"{symptom.symptom_name}: improvement {symptom.improvement_level}/10",
                improvement_level=symptom.improvement_level,
                person_id=third_party_id,
                person_name=person_name
            ))
            symptoms_data.append({
                "symptom_name": symptom.symptom_name,
                "improvement_level": symptom.improvement_level,
                "recorded_at": symptom.recorded_at.isoformat()
            })

        # Create medication journey
        medication_journeys.append(MedicationJourney(
            medication_id=med.id,
            medication_name=med.drug_name,
            start_date=med.start_date,
            end_date=med.end_date,
            person_id=third_party_id,
            person_name=person_name,
            logs_count=len(logs),
            side_effects=side_effects_data,
            symptoms_treated=symptoms_data,
            color=med_color,
            is_active=med.active
        ))

    # Sort events chronologically
    events.sort(key=lambda e: e.timestamp)

    # Build symptom-medication correlations
    symptom_correlations = []

    # Get all symptoms for medications in this time period
    all_symptoms = db.query(SymptomTracking).join(
        Medication, SymptomTracking.medication_id == Medication.id
    ).filter(
        and_(
            SymptomTracking.user_id == current_user.id,
            SymptomTracking.recorded_at >= start_date,
            SymptomTracking.recorded_at <= end_date
        )
    )

    if third_party_id is not None:
        all_symptoms = all_symptoms.filter(Medication.third_party_id == third_party_id)
    else:
        all_symptoms = all_symptoms.filter(Medication.third_party_id.is_(None))

    all_symptoms = all_symptoms.all()

    # Group by symptom name
    symptom_groups = defaultdict(list)
    for symptom in all_symptoms:
        symptom_groups[symptom.symptom_name].append(symptom)

    for symptom_name, symptom_list in symptom_groups.items():
        # Group by medication
        med_improvements = defaultdict(list)
        for symptom in symptom_list:
            med = db.query(Medication).filter(Medication.id == symptom.medication_id).first()
            if med:
                med_improvements[med.drug_name].append(symptom.improvement_level)

        # Calculate averages and trends
        medications_data = []
        overall_improvements = []

        for med_name, improvements in med_improvements.items():
            avg_improvement = sum(improvements) / len(improvements)
            overall_improvements.extend(improvements)

            # Determine trend
            if len(improvements) >= 2:
                mid = len(improvements) // 2
                first_half = sum(improvements[:mid]) / mid
                second_half = sum(improvements[mid:]) / (len(improvements) - mid)

                if second_half > first_half + 1:
                    trend = "improving"
                elif second_half < first_half - 1:
                    trend = "worsening"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"

            medications_data.append({
                "medication_name": med_name,
                "average_improvement": round(avg_improvement, 2),
                "data_points": len(improvements),
                "trend": trend
            })

        avg_overall = sum(overall_improvements) / len(overall_improvements) if overall_improvements else 0

        # Overall trend
        if len(overall_improvements) >= 2:
            mid = len(overall_improvements) // 2
            first_half = sum(overall_improvements[:mid]) / mid
            second_half = sum(overall_improvements[mid:]) / (len(overall_improvements) - mid)
            overall_trend = "improving" if second_half > first_half + 1 else "worsening" if second_half < first_half - 1 else "stable"
        else:
            overall_trend = "insufficient_data"

        symptom_correlations.append(SymptomMedicationCorrelation(
            symptom_name=symptom_name,
            medications=medications_data,
            average_improvement=round(avg_overall, 2),
            trend=overall_trend
        ))

    # Build medication-side effect correlations
    med_side_effect_correlations = []

    for med in medications:
        side_effects = db.query(SideEffect).filter(
            and_(
                SideEffect.medication_id == med.id,
                SideEffect.occurred_at >= start_date,
                SideEffect.occurred_at <= end_date
            )
        ).all()

        if side_effects:
            severity_dist = {"mild": 0, "moderate": 0, "severe": 0}
            side_effects_data = []

            for se in side_effects:
                severity_dist[se.severity.value] += 1
                side_effects_data.append({
                    "description": se.description,
                    "severity": se.severity.value,
                    "occurred_at": se.occurred_at.isoformat()
                })

            med_side_effect_correlations.append(MedicationSideEffectCorrelation(
                medication_id=med.id,
                medication_name=med.drug_name,
                person_name=person_name,
                side_effects=side_effects_data,
                side_effect_count=len(side_effects),
                severity_distribution=severity_dist
            ))

    # Get total counts
    total_logs = db.query(func.count(MedicationLog.id)).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).filter(
        and_(
            MedicationLog.user_id == current_user.id,
            MedicationLog.taken_at >= start_date,
            MedicationLog.taken_at <= end_date
        )
    )

    if third_party_id is not None:
        total_logs = total_logs.filter(Medication.third_party_id == third_party_id)
    else:
        total_logs = total_logs.filter(Medication.third_party_id.is_(None))

    total_logs = total_logs.scalar()

    total_side_effects = len([e for e in events if e.event_type == "side_effect"])
    total_symptoms = len([e for e in events if e.event_type == "symptom"])

    return JourneyTimeline(
        person_id=third_party_id,
        person_name=person_name,
        period_start=start_date,
        period_end=end_date,
        events=events,
        medications=medication_journeys,
        symptom_medication_correlations=symptom_correlations,
        medication_side_effect_correlations=med_side_effect_correlations,
        total_medications=len(medications),
        total_logs=total_logs,
        total_side_effects=total_side_effects,
        total_symptoms_tracked=total_symptoms
    )
