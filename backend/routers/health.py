import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import User, HealthReport, TastePreference
from core.schemas import (
    StandardResponse,
    HealthReportCreate,
    HealthReportUpdate,
    HealthAnalysisRequest,
)
from core.llm_client import llm_client


router = APIRouter(
    prefix="/health",
    tags=["health"]
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
        "creatinine": report.creatinine,
        "bun": report.bun,
        "alt": report.alt,
        "ast": report.ast,
        "hemoglobin": report.hemoglobin,
        "notes": report.notes,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


def serialize_preference(preference: TastePreference | None):
    if not preference:
        return None

    return {
        "preferred_flavors": preference.preferred_flavors,
        "disliked_foods": preference.disliked_foods,
        "preferred_cuisines": preference.preferred_cuisines,
        "allergies": preference.allergies,
        "cooking_time_limit": preference.cooking_time_limit,
        "difficulty_preference": preference.difficulty_preference,
        "budget_level": preference.budget_level,
        "meal_count": preference.meal_count,
    }


def build_analysis_prompt(data_source: dict) -> str:
    data_text = json.dumps(data_source, ensure_ascii=False, indent=2)

    return f"""
你是一名专业、谨慎的 AI 营养师。

请根据下面的用户基础信息、体检报告和口味偏好，生成一份个性化健康饮食分析。

【分析数据来源】
{data_text}

请严格按照以下结构输出：

一、核心结论
- 简要总结用户目前主要健康风险。
- 明确说明分析基于本次提供的体检报告，不要编造不存在的指标。

二、体检指标解读
- 对血糖、血脂、血压、尿酸、肝肾功能等已提供指标进行解读。
- 如果某个指标没有提供，请说明“该指标未提供，暂不判断”。

三、饮食控制原则
- 根据用户异常指标提出饮食原则。
- 如低盐、低脂、控糖、低嘌呤、控制总热量等。

四、推荐食物
- 给出适合用户的主食、蔬菜、水果、蛋白质、饮品建议。

五、避免或限制食物
- 给出需要少吃或避免的食物。
- 如果用户有过敏或忌口，要重点提醒。

六、一日三餐示例
- 结合用户口味偏好给出早餐、午餐、晚餐建议。

七、重要提醒
- 提醒用户定期复查。
- 明确说明本建议不能替代医生诊断和治疗。
"""


def build_data_source(user: User, report: HealthReport, preference: TastePreference | None):
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "gender": user.gender,
            "age": user.age,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "bmi": user.bmi,
            "health_goals": user.health_goals,
        },
        "health_report": serialize_report(report),
        "taste_preferences": serialize_preference(preference),
    }


@router.get("/", response_model=StandardResponse)
def old_list_health_reports(db: Session = Depends(get_db)):
    """
    兼容旧接口：GET /health/
    """
    reports = db.query(HealthReport).order_by(HealthReport.created_at.desc()).all()

    return StandardResponse(
        success=True,
        message="获取体检报告列表成功",
        data=[serialize_report(report) for report in reports]
    )


@router.get("/reports", response_model=StandardResponse)
def list_health_reports(user_id: int | None = None, db: Session = Depends(get_db)):
    """
    新接口：GET /health/reports
    可选参数：?user_id=1
    """
    query = db.query(HealthReport)

    if user_id is not None:
        query = query.filter(HealthReport.user_id == user_id)

    reports = query.order_by(HealthReport.created_at.desc()).all()

    return StandardResponse(
        success=True,
        message="获取体检报告列表成功",
        data=[serialize_report(report) for report in reports]
    )


@router.get("/reports/{report_id}", response_model=StandardResponse)
def get_health_report(report_id: int, db: Session = Depends(get_db)):
    """
    新接口：GET /health/reports/{report_id}
    """
    report = db.query(HealthReport).filter(HealthReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")

    return StandardResponse(
        success=True,
        message="获取体检报告详情成功",
        data=serialize_report(report)
    )


@router.post("/", response_model=StandardResponse)
def old_create_health_report(payload: HealthReportCreate, db: Session = Depends(get_db)):
    """
    兼容旧接口：POST /health/
    """
    return create_health_report(payload, db)


@router.post("/reports", response_model=StandardResponse)
def create_health_report(payload: HealthReportCreate, db: Session = Depends(get_db)):
    """
    新接口：POST /health/reports
    """
    user = db.query(User).filter(User.id == payload.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    data = payload.model_dump()

    if not data.get("report_name"):
        data["report_name"] = f"{user.username}的体检报告"

    report = HealthReport(**data)

    db.add(report)
    db.commit()
    db.refresh(report)

    return StandardResponse(
        success=True,
        message="体检报告创建成功",
        data=serialize_report(report)
    )


@router.put("/reports/{report_id}", response_model=StandardResponse)
def update_health_report(
    report_id: int,
    payload: HealthReportUpdate,
    db: Session = Depends(get_db)
):
    """
    新接口：PUT /health/reports/{report_id}
    """
    report = db.query(HealthReport).filter(HealthReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(report, key, value)

    db.commit()
    db.refresh(report)

    return StandardResponse(
        success=True,
        message="体检报告更新成功",
        data=serialize_report(report)
    )


@router.delete("/reports/{report_id}", response_model=StandardResponse)
def delete_health_report(report_id: int, db: Session = Depends(get_db)):
    """
    新接口:DELETE /health/reports/{report_id}
    """
    report = db.query(HealthReport).filter(HealthReport.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="体检报告不存在")

    db.delete(report)
    db.commit()

    return StandardResponse(
        success=True,
        message="体检报告删除成功",
        data={"id": report_id}
    )


@router.post("/analyze", response_model=StandardResponse)
async def analyze_health(payload: HealthAnalysisRequest, db: Session = Depends(get_db)):
    """
    新接口:POST /health/analyze

    必须传 user_id 和 report_id。
    不再默认使用测试数据。
    """
    user = db.query(User).filter(User.id == payload.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    report = db.query(HealthReport).filter(
        HealthReport.id == payload.report_id,
        HealthReport.user_id == payload.user_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="请先录入体检报告，再进行 AI 健康分析"
        )

    preference = db.query(TastePreference).filter(
    TastePreference.user_id == payload.user_id,
    TastePreference.is_default == 1
    ).first()

    if not preference:
        preference = db.query(TastePreference).filter(
            TastePreference.user_id == payload.user_id
        ).order_by(TastePreference.updated_at.desc()).first()

    data_source = build_data_source(user, report, preference)
    prompt = build_analysis_prompt(data_source)

    try:
        analysis = await llm_client.chat(
            messages=[
                {
                    "role": "system",
                    "content": "你是一名专业、谨慎的 AI 营养师，只能基于用户提供的体检报告和偏好进行分析。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=2000
        )

        return StandardResponse(
            success=True,
            message="AI健康分析成功",
            data={
                "data_source": data_source,
                "analysis": analysis
            }
        )

    except Exception as e:
        return StandardResponse(
            success=False,
            message=f"AI健康分析失败:{str(e)}",
            data={
                "data_source": data_source,
                "analysis": "AI健康分析服务暂时不可用,请检查大模型 API 配置。"
            }
        )


@router.get("/{user_id}", response_model=StandardResponse)
def old_get_health_report_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    兼容旧接口:GET /health/{user_id}
    注意：这个接口放在最后，避免影响 /health/reports 等新接口。
    """
    reports = db.query(HealthReport).filter(
        HealthReport.user_id == user_id
    ).order_by(HealthReport.created_at.desc()).all()

    if not reports:
        raise HTTPException(status_code=404, detail="该用户暂无体检报告")

    return StandardResponse(
        success=True,
        message="获取用户体检报告成功",
        data=[serialize_report(report) for report in reports]
    )