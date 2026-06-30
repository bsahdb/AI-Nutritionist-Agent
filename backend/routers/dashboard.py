from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import User, HealthReport, TastePreference, MealPlan
from core.schemas import StandardResponse


router = APIRouter(
    prefix="/dashboard",
    tags=["数据看板"]
)


def serialize_report(report: HealthReport):
    return {
        "id": report.id,
        "user_id": report.user_id,
        "report_name": report.report_name,
        "fasting_glucose": report.fasting_glucose,
        "postprandial_glucose": report.postprandial_glucose,
        "total_cholesterol": report.total_cholesterol,
        "triglycerides": report.triglycerides,
        "hdl_cholesterol": report.hdl_cholesterol,
        "ldl_cholesterol": report.ldl_cholesterol,
        "systolic_bp": report.systolic_bp,
        "diastolic_bp": report.diastolic_bp,
        "uric_acid": report.uric_acid,
        "notes": report.notes,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


def serialize_meal_plan(plan: MealPlan):
    return {
        "id": plan.id,
        "user_id": plan.user_id,
        "title": plan.title,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
    }


@router.get("/summary", response_model=StandardResponse)
def get_dashboard_summary(user_id: int | None = None, db: Session = Depends(get_db)):
    user_query = db.query(User)
    report_query = db.query(HealthReport)
    preference_query = db.query(TastePreference)
    meal_plan_query = db.query(MealPlan)

    if user_id is not None:
        report_query = report_query.filter(HealthReport.user_id == user_id)
        preference_query = preference_query.filter(TastePreference.user_id == user_id)
        meal_plan_query = meal_plan_query.filter(MealPlan.user_id == user_id)

    recent_reports = report_query.order_by(
        HealthReport.created_at.desc()
    ).limit(5).all()

    recent_plans = meal_plan_query.order_by(
        MealPlan.created_at.desc()
    ).limit(5).all()

    high_uric_acid_count = report_query.filter(
        HealthReport.uric_acid != None,
        HealthReport.uric_acid > 420
    ).count()

    high_bp_count = report_query.filter(
        HealthReport.systolic_bp != None,
        HealthReport.diastolic_bp != None,
        (HealthReport.systolic_bp >= 130) | (HealthReport.diastolic_bp >= 85)
    ).count()

    high_lipid_count = report_query.filter(
        (
            (HealthReport.total_cholesterol != None) &
            (HealthReport.total_cholesterol >= 5.2)
        ) |
        (
            (HealthReport.triglycerides != None) &
            (HealthReport.triglycerides >= 1.7)
        ) |
        (
            (HealthReport.ldl_cholesterol != None) &
            (HealthReport.ldl_cholesterol >= 3.4)
        )
    ).count()

    high_glucose_count = report_query.filter(
        (
            (HealthReport.fasting_glucose != None) &
            (HealthReport.fasting_glucose >= 6.1)
        ) |
        (
            (HealthReport.postprandial_glucose != None) &
            (HealthReport.postprandial_glucose >= 7.8)
        )
    ).count()

    data = {
        "stats": {
            "user_count": user_query.count(),
            "health_report_count": report_query.count(),
            "preference_count": preference_query.count(),
            "meal_plan_count": meal_plan_query.count(),
        },
        "recent_health_reports": [
            serialize_report(report) for report in recent_reports
        ],
        "recent_meal_plans": [
            serialize_meal_plan(plan) for plan in recent_plans
        ],
        "risk_summary": {
            "high_uric_acid_count": high_uric_acid_count,
            "high_bp_count": high_bp_count,
            "high_lipid_count": high_lipid_count,
            "high_glucose_count": high_glucose_count,
        }
    }

    return StandardResponse(
        success=True,
        message="获取数据看板成功",
        data=data
    )