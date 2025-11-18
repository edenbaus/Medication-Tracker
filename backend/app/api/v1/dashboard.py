"""Dashboard API endpoints."""
from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.medication import Medication
from app.models.medication_log import MedicationLog
from app.models.side_effect import SideEffect
from app.models.symptom import SymptomTracking
from app.models.third_party import ThirdParty
from app.schemas.dashboard import (
    DashboardSummary,
    PersonStats,
    RecentActivity,
    MedicationSummary,
    RefillAlert,
)

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive dashboard summary."""
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_ago = now - timedelta(days=7)

    # Get all third parties for this user
    third_parties = db.query(ThirdParty).filter(
        ThirdParty.user_id == current_user.id
    ).all()

    # Overall statistics
    total_active_medications = db.query(Medication).filter(
        Medication.user_id == current_user.id,
        Medication.active == True,
    ).count()

    total_logs_today = db.query(MedicationLog).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).filter(
        Medication.user_id == current_user.id,
        MedicationLog.taken_at >= today_start,
    ).count()

    total_logs_7days = db.query(MedicationLog).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).filter(
        Medication.user_id == current_user.id,
        MedicationLog.taken_at >= week_ago,
    ).count()

    total_side_effects_7days = db.query(SideEffect).filter(
        SideEffect.user_id == current_user.id,
        SideEffect.occurred_at >= week_ago,
    ).count()

    total_symptoms_tracked_7days = db.query(SymptomTracking).filter(
        SymptomTracking.user_id == current_user.id,
        SymptomTracking.recorded_at >= week_ago,
    ).count()

    # Per-person statistics
    people_stats: List[PersonStats] = []

    # Stats for current user (Me)
    my_active_meds = db.query(Medication).filter(
        Medication.user_id == current_user.id,
        Medication.third_party_id.is_(None),
        Medication.active == True,
    ).count()

    my_logs_7days = db.query(MedicationLog).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).filter(
        Medication.user_id == current_user.id,
        Medication.third_party_id.is_(None),
        MedicationLog.taken_at >= week_ago,
    ).count()

    my_side_effects_7days = db.query(SideEffect).join(
        Medication, SideEffect.medication_id == Medication.id
    ).filter(
        SideEffect.user_id == current_user.id,
        Medication.third_party_id.is_(None),
        SideEffect.occurred_at >= week_ago,
    ).count()

    my_symptoms_7days = db.query(SymptomTracking).join(
        Medication, SymptomTracking.medication_id == Medication.id
    ).filter(
        SymptomTracking.user_id == current_user.id,
        Medication.third_party_id.is_(None),
        SymptomTracking.recorded_at >= week_ago,
    ).count()

    people_stats.append(
        PersonStats(
            person_id=None,
            person_name="Me",
            active_medications=my_active_meds,
            total_logs_7days=my_logs_7days,
            side_effects_7days=my_side_effects_7days,
            symptoms_tracked_7days=my_symptoms_7days,
        )
    )

    # Stats for each third party
    for tp in third_parties:
        tp_active_meds = db.query(Medication).filter(
            Medication.user_id == current_user.id,
            Medication.third_party_id == tp.id,
            Medication.active == True,
        ).count()

        tp_logs_7days = db.query(MedicationLog).join(
            Medication, MedicationLog.medication_id == Medication.id
        ).filter(
            Medication.user_id == current_user.id,
            Medication.third_party_id == tp.id,
            MedicationLog.taken_at >= week_ago,
        ).count()

        tp_side_effects_7days = db.query(SideEffect).join(
            Medication, SideEffect.medication_id == Medication.id
        ).filter(
            SideEffect.user_id == current_user.id,
            Medication.third_party_id == tp.id,
            SideEffect.occurred_at >= week_ago,
        ).count()

        tp_symptoms_7days = db.query(SymptomTracking).join(
            Medication, SymptomTracking.medication_id == Medication.id
        ).filter(
            SymptomTracking.user_id == current_user.id,
            Medication.third_party_id == tp.id,
            SymptomTracking.recorded_at >= week_ago,
        ).count()

        people_stats.append(
            PersonStats(
                person_id=tp.id,
                person_name=tp.name,
                active_medications=tp_active_meds,
                total_logs_7days=tp_logs_7days,
                side_effects_7days=tp_side_effects_7days,
                symptoms_tracked_7days=tp_symptoms_7days,
            )
        )

    # Recent activity (last 10 events)
    recent_activity: List[RecentActivity] = []

    # Get recent logs
    recent_logs = db.query(
        MedicationLog.id,
        MedicationLog.taken_at,
        Medication.drug_name,
        Medication.third_party_id,
    ).join(
        Medication, MedicationLog.medication_id == Medication.id
    ).filter(
        Medication.user_id == current_user.id
    ).order_by(
        MedicationLog.taken_at.desc()
    ).limit(5).all()

    for log in recent_logs:
        person_name = "Me"
        if log.third_party_id:
            tp = next((tp for tp in third_parties if tp.id == log.third_party_id), None)
            if tp:
                person_name = tp.name

        recent_activity.append(
            RecentActivity(
                id=log.id,
                activity_type="log",
                timestamp=log.taken_at,
                description=f"Logged dose of {log.drug_name}",
                medication_name=log.drug_name,
                person_id=log.third_party_id,
                person_name=person_name,
            )
        )

    # Get recent side effects
    recent_side_effects = db.query(
        SideEffect.id,
        SideEffect.occurred_at,
        SideEffect.description,
        SideEffect.severity,
        Medication.drug_name,
        Medication.third_party_id,
    ).join(
        Medication, SideEffect.medication_id == Medication.id
    ).filter(
        SideEffect.user_id == current_user.id
    ).order_by(
        SideEffect.occurred_at.desc()
    ).limit(3).all()

    for se in recent_side_effects:
        person_name = "Me"
        if se.third_party_id:
            tp = next((tp for tp in third_parties if tp.id == se.third_party_id), None)
            if tp:
                person_name = tp.name

        recent_activity.append(
            RecentActivity(
                id=se.id,
                activity_type="side_effect",
                timestamp=se.occurred_at,
                description=f"Side effect reported: {se.description[:50]}...",
                medication_name=se.drug_name,
                severity=se.severity,
                person_id=se.third_party_id,
                person_name=person_name,
            )
        )

    # Get recent symptoms
    recent_symptoms = db.query(
        SymptomTracking.id,
        SymptomTracking.recorded_at,
        SymptomTracking.symptom_name,
        SymptomTracking.improvement_level,
        Medication.drug_name,
        Medication.third_party_id,
    ).join(
        Medication, SymptomTracking.medication_id == Medication.id
    ).filter(
        SymptomTracking.user_id == current_user.id
    ).order_by(
        SymptomTracking.recorded_at.desc()
    ).limit(2).all()

    for symptom in recent_symptoms:
        person_name = "Me"
        if symptom.third_party_id:
            tp = next((tp for tp in third_parties if tp.id == symptom.third_party_id), None)
            if tp:
                person_name = tp.name

        recent_activity.append(
            RecentActivity(
                id=symptom.id,
                activity_type="symptom",
                timestamp=symptom.recorded_at,
                description=f"Tracked symptom: {symptom.symptom_name} (Improvement: {symptom.improvement_level}/10)",
                medication_name=symptom.drug_name,
                person_id=symptom.third_party_id,
                person_name=person_name,
            )
        )

    # Sort all activity by timestamp
    recent_activity.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activity = recent_activity[:10]

    # Medications needing attention (active meds not logged in 3+ days)
    three_days_ago = now - timedelta(days=3)
    medications_needing_attention: List[MedicationSummary] = []

    active_meds = db.query(Medication).filter(
        Medication.user_id == current_user.id,
        Medication.active == True,
    ).all()

    for med in active_meds:
        last_log = db.query(MedicationLog).filter(
            MedicationLog.medication_id == med.id
        ).order_by(
            MedicationLog.taken_at.desc()
        ).first()

        total_logs = db.query(MedicationLog).filter(
            MedicationLog.medication_id == med.id
        ).count()

        person_name = "Me"
        if med.third_party_id:
            tp = next((tp for tp in third_parties if tp.id == med.third_party_id), None)
            if tp:
                person_name = tp.name

        if last_log:
            days_since = (now - last_log.taken_at).days
            if days_since >= 3:
                medications_needing_attention.append(
                    MedicationSummary(
                        medication_id=med.id,
                        medication_name=med.drug_name,
                        last_logged=last_log.taken_at,
                        days_since_last_log=days_since,
                        total_logs=total_logs,
                        is_active=med.active,
                        person_id=med.third_party_id,
                        person_name=person_name,
                    )
                )
        else:
            # Never logged
            medications_needing_attention.append(
                MedicationSummary(
                    medication_id=med.id,
                    medication_name=med.drug_name,
                    last_logged=None,
                    days_since_last_log=None,
                    total_logs=0,
                    is_active=med.active,
                    person_id=med.third_party_id,
                    person_name=person_name,
                )
            )

    # Sort by days since last log (descending)
    medications_needing_attention.sort(
        key=lambda x: x.days_since_last_log if x.days_since_last_log is not None else 999,
        reverse=True
    )

    # Get medications due for refill (within 7 days or overdue)
    refill_alerts: List[RefillAlert] = []

    # Get all active medications with refill tracking info
    refill_meds = db.query(Medication).filter(
        Medication.user_id == current_user.id,
        Medication.active == True,
        Medication.date_filled.isnot(None),
        Medication.days_supply.isnot(None),
    ).all()

    for med in refill_meds:
        person_name = "Me"
        if med.third_party_id:
            tp = next((tp for tp in third_parties if tp.id == med.third_party_id), None)
            if tp:
                person_name = tp.name

        # Check if due for refill
        if med.is_due_for_refill:
            refill_alerts.append(
                RefillAlert(
                    medication_id=med.id,
                    medication_name=med.drug_name,
                    refill_date=med.refill_date,
                    days_until_refill=med.days_until_refill,
                    refills_remaining=med.refills_remaining,
                    date_filled=med.date_filled,
                    days_supply=med.days_supply,
                    person_id=med.third_party_id,
                    person_name=person_name,
                )
            )

    # Sort by days_until_refill (soonest first)
    refill_alerts.sort(key=lambda x: x.days_until_refill)

    return DashboardSummary(
        user_name=current_user.username or current_user.email,
        total_active_medications=total_active_medications,
        total_logs_today=total_logs_today,
        total_logs_7days=total_logs_7days,
        total_side_effects_7days=total_side_effects_7days,
        total_symptoms_tracked_7days=total_symptoms_tracked_7days,
        people_stats=people_stats,
        recent_activity=recent_activity,
        medications_needing_attention=medications_needing_attention,
        refill_alerts=refill_alerts,
    )
