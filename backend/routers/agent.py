import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from openai import OpenAI

from core.database import get_db
from core.models import User, HealthReport, TastePreference
from core.schemas import StandardResponse, AgentRequest


load_dotenv()

router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)


def get_llm_client() -> OpenAI:
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")

    if not api_key:
        raise RuntimeError("LLM_API_KEY 未配置，请检查 backend/.env")

    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )


def build_user_profile(
    user: User | None,
    health_reports: List[HealthReport],
    preference: TastePreference | None
) -> Dict[str, Any]:
    user_info = {}

    if user:
        user_info = {
            "id": user.id,
            "username": user.username,
            "gender": user.gender,
            "age": user.age,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "health_goals": user.health_goals,
        }

    reports = []
    for report in health_reports:
        reports.append({
            "id": report.id,
            "user_id": report.user_id,
            "report_name": report.report_name,
            "created_at": report.created_at.isoformat() if report.created_at else None,
            "fasting_glucose": report.fasting_glucose,
            "postprandial_glucose": report.postprandial_glucose,
            "total_cholesterol": report.total_cholesterol,
            "triglycerides": report.triglycerides,
            "hdl_cholesterol": report.hdl_cholesterol,
            "ldl_cholesterol": report.ldl_cholesterol,
            "systolic_bp": report.systolic_bp,
            "diastolic_bp": report.diastolic_bp,
            "uric_acid": report.uric_acid,
            "creatinine": getattr(report, "creatinine", None),
            "bun": getattr(report, "bun", None),
            "alt": report.alt,
            "ast": report.ast,
            "hemoglobin": report.hemoglobin,
            "notes": report.notes,
        })

    preference_info = {}

    if preference:
        preference_info = {
            "preferred_flavors": preference.preferred_flavors,
            "disliked_foods": preference.disliked_foods,
            "preferred_cuisines": preference.preferred_cuisines,
            "allergies": preference.allergies,
            "cooking_time_limit": preference.cooking_time_limit,
            "difficulty_preference": preference.difficulty_preference,
            "budget_level": preference.budget_level,
            "meal_count": preference.meal_count,
        }

    return {
        "user": user_info,
        "health_reports": reports,
        "taste_preferences": preference_info
    }


def call_llm(user_question: str, profile: Dict[str, Any]) -> str:
    client = get_llm_client()

    model = os.getenv("LLM_MODEL", "deepseek-chat")

    system_prompt = """
你是一名专业、谨慎的AI营养师助手。
你需要根据用户基础信息、体检报告、口味偏好，给出个性化饮食建议。

回答要求：
1. 用中文回答。
2. 先给出结论，再给出具体建议。
3. 如果涉及高血压、糖尿病、高尿酸、高血脂等问题，要给出饮食原则和食物建议。
4. 不要声称可以替代医生诊断。
5. 如果用户指标异常，要提醒定期复查和咨询医生。
6. 回答要实用，可以包含早餐、午餐、晚餐建议。
"""

    user_prompt = f"""
用户问题：
{user_question}

用户健康档案：
{profile}

请基于以上信息，给出专业、实用、个性化的营养建议。
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.4,
        max_tokens=1200
    )

    return response.choices[0].message.content or "抱歉，我暂时无法生成回答。"


@router.post("/chat", response_model=StandardResponse)
def chat_with_agent(payload: AgentRequest, db: Session = Depends(get_db)):
    user_id = payload.user_id or 1

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return StandardResponse(
            success=False,
            message="用户不存在",
            data={
                "reply": "用户不存在，请先创建用户。"
            }
        )

    report_id = None

    if payload.context and payload.context.get("report_id"):
        try:
            report_id = int(payload.context.get("report_id"))
        except Exception:
            report_id = None

    if report_id:
        report = db.query(HealthReport).filter(
            HealthReport.id == report_id,
            HealthReport.user_id == user_id
        ).first()

        if not report:
            return StandardResponse(
                success=False,
                message="当前选择的体检报告不存在",
                data={
                    "reply": "当前选择的体检报告不存在，请重新选择体检报告。"
                }
            )

        health_reports = [report]
    else:
        health_reports = db.query(HealthReport).filter(
            HealthReport.user_id == user_id
        ).order_by(HealthReport.created_at.desc()).limit(1).all()

    preference = db.query(TastePreference).filter(
    TastePreference.user_id == payload.user_id,
    TastePreference.is_default == 1
    ).first()

    if not preference:
        preference = db.query(TastePreference).filter(
            TastePreference.user_id == payload.user_id
        ).order_by(TastePreference.updated_at.desc()).first()

    profile = build_user_profile(user, health_reports, preference)

    try:
        reply = call_llm(payload.message, profile)

        return StandardResponse(
            success=True,
            message="Agent回复成功",
            data={
                "reply": reply,
                "report_id": report_id,
                "profile": profile
            }
        )

    except Exception as e:
        return StandardResponse(
            success=False,
            message=f"LLM调用失败:{str(e)}",
            data={
                "reply": "抱歉,AI营养师服务暂时不可用,请检查大模型API配置。"
            }
        )


@router.get("/health", response_model=StandardResponse)
def agent_health_check():
    return StandardResponse(
        success=True,
        message="Agent服务正常",
        data={
            "status": "ok"
        }
    )