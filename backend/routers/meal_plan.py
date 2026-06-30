import json
import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import MealPlan, HealthReport, TastePreference, User
from core.schemas import StandardResponse, MealPlanGenerateRequest
from core.llm_client import llm_client


router = APIRouter(prefix="/meal-plans", tags=["饮食计划"])


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


def serialize_preference(pref: TastePreference | None):
    if not pref:
        return None

    return {
        "preferred_flavors": pref.preferred_flavors or [],
        "disliked_foods": pref.disliked_foods or [],
        "preferred_cuisines": pref.preferred_cuisines or [],
        "allergies": pref.allergies or [],
        "cooking_time_limit": pref.cooking_time_limit,
        "difficulty_preference": pref.difficulty_preference,
        "budget_level": pref.budget_level,
        "meal_count": pref.meal_count,
    }


def serialize_plan(plan: MealPlan):
    return {
        "id": plan.id,
        "user_id": plan.user_id,
        "title": plan.title,
        "health_summary": plan.health_summary,
        "nutrition_goals": plan.nutrition_goals,
        "plan_data": plan.plan_data,
        "shopping_list": plan.shopping_list,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
    }


def build_data_source(user: User, report: HealthReport, pref: TastePreference | None):
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "gender": user.gender,
            "age": user.age,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "bmi": user.bmi,
            "health_goals": user.health_goals or [],
        },
        "health_report": serialize_report(report),
        "taste_preferences": serialize_preference(pref),
    }


def build_meal_plan_prompt(data_source: dict, req: MealPlanGenerateRequest):
    data_text = json.dumps(data_source, ensure_ascii=False, indent=2)

    return f"""
你是一名专业、谨慎的 AI 营养师。

请根据以下用户基础信息、体检报告和口味偏好，生成个性化饮食计划。

【数据来源】
{data_text}

【生成要求】
- 生成天数：{req.days} 天
- 每日餐次：{req.meal_count} 餐
- 目标热量：{req.target_calories if req.target_calories else "未指定"}
- 额外要求：{req.requirements or "无"}

请严格输出 JSON，不要输出 Markdown，不要输出解释文字。

JSON 格式如下：
{{
  "title": "饮食计划标题",
  "health_summary": {{
    "main_risks": ["主要健康风险1", "主要健康风险2"],
    "summary": "健康概况总结"
  }},
  "nutrition_goals": {{
    "calorie_target": "热量目标",
    "protein": "蛋白质建议",
    "fat": "脂肪建议",
    "carbohydrate": "碳水建议",
    "special_goals": ["低盐", "低脂"]
  }},
  "days": [
    {{
      "day": 1,
      "theme": "当天饮食主题",
      "meals": [
        {{
          "meal": "早餐",
          "foods": ["食物1", "食物2"],
          "notes": "这一餐的营养说明"
        }},
        {{
          "meal": "午餐",
          "foods": ["食物1", "食物2"],
          "notes": "这一餐的营养说明"
        }},
        {{
          "meal": "晚餐",
          "foods": ["食物1", "食物2"],
          "notes": "这一餐的营养说明"
        }}
      ],
      "tips": ["当天注意事项1", "当天注意事项2"]
    }}
  ],
  "shopping_list": ["食材1", "食材2"]
}}

要求：
1. 必须结合体检报告中的异常指标。
2. 必须结合口味偏好、忌口和过敏信息。
3. 不要推荐用户过敏或明确不喜欢的食物。
4. 如果有高尿酸，注意低嘌呤。
5. 如果有血压偏高，注意低盐。
6. 如果有血脂异常，注意低脂、高纤维。
7. 本计划不能替代医生诊断。
"""


def extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)

    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return {}


@router.post("/generate", response_model=StandardResponse)
async def generate_meal_plan(req: MealPlanGenerateRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == req.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    report = db.query(HealthReport).filter(
        HealthReport.id == req.report_id,
        HealthReport.user_id == req.user_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="请先选择有效的体检报告")

    preference = db.query(TastePreference).filter(
    TastePreference.user_id == req.user_id,
    TastePreference.is_default == 1
    ).first()

    if not preference:
        preference = db.query(TastePreference).filter(
            TastePreference.user_id == req.user_id
        ).order_by(TastePreference.updated_at.desc()).first()

    data_source = build_data_source(user, report, preference)
    prompt = build_meal_plan_prompt(data_source, req)

    try:
        result = await llm_client.chat(
            messages=[
                {
                    "role": "system",
                    "content": "你是一名专业营养师，请严格输出合法 JSON。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=4000
        )
    except Exception as e:
        return StandardResponse(
            success=False,
            message=f"饮食计划生成失败：{str(e)}",
            data=None
        )

    plan_json = extract_json(result)

    if not plan_json:
        plan_json = {
            "title": req.title or "AI个性化饮食计划",
            "health_summary": {
                "summary": "AI 返回内容无法解析为标准 JSON，已保存原始内容。"
            },
            "nutrition_goals": {},
            "days": [],
            "shopping_list": [],
            "raw_text": result
        }

    title = req.title or plan_json.get("title") or f"{req.days}天个性化饮食计划"

    meal_plan = MealPlan(
        user_id=req.user_id,
        title=title,
        health_summary=plan_json.get("health_summary"),
        nutrition_goals=plan_json.get("nutrition_goals"),
        plan_data={
            "data_source": data_source,
            "days": plan_json.get("days", []),
            "raw_text": plan_json.get("raw_text")
        },
        shopping_list=plan_json.get("shopping_list", [])
    )

    db.add(meal_plan)
    db.commit()
    db.refresh(meal_plan)

    return StandardResponse(
        success=True,
        message="饮食计划生成成功",
        data=serialize_plan(meal_plan)
    )


@router.get("", response_model=StandardResponse)
def list_meal_plans(user_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(MealPlan)

    if user_id is not None:
        query = query.filter(MealPlan.user_id == user_id)

    plans = query.order_by(MealPlan.created_at.desc()).all()

    return StandardResponse(
        success=True,
        message="获取饮食计划列表成功",
        data=[serialize_plan(plan) for plan in plans]
    )


@router.get("/{plan_id}", response_model=StandardResponse)
def get_meal_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="饮食计划不存在")

    return StandardResponse(
        success=True,
        message="获取饮食计划详情成功",
        data=serialize_plan(plan)
    )


@router.delete("/{plan_id}", response_model=StandardResponse)
def delete_meal_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404, detail="饮食计划不存在")

    db.delete(plan)
    db.commit()

    return StandardResponse(
        success=True,
        message="饮食计划删除成功",
        data={"id": plan_id}
    )