from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class StandardResponse(BaseModel):
    success: bool = True
    message: str = "success"
    data: Optional[Any] = None


# =========================
# 用户相关 Schema
# =========================

class UserBase(BaseModel):
    username: str
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    health_goals: Optional[List[str]] = Field(default_factory=list)


class UserCreate(UserBase):
    password: Optional[str] = None
    password_hash: Optional[str] = None


class UserUpdate(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    health_goals: Optional[List[str]] = None


class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =========================
# 体检报告相关 Schema
# =========================

class HealthReportBase(BaseModel):
    user_id: int
    report_name: Optional[str] = None

    fasting_glucose: Optional[float] = None
    postprandial_glucose: Optional[float] = None

    total_cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None
    hdl_cholesterol: Optional[float] = None
    ldl_cholesterol: Optional[float] = None

    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None

    uric_acid: Optional[float] = None
    creatinine: Optional[float] = None
    bun: Optional[float] = None

    alt: Optional[float] = None
    ast: Optional[float] = None
    hemoglobin: Optional[float] = None

    notes: Optional[str] = None


class HealthReportCreate(HealthReportBase):
    pass


class HealthReportUpdate(BaseModel):
    report_name: Optional[str] = None

    fasting_glucose: Optional[float] = None
    postprandial_glucose: Optional[float] = None

    total_cholesterol: Optional[float] = None
    triglycerides: Optional[float] = None
    hdl_cholesterol: Optional[float] = None
    ldl_cholesterol: Optional[float] = None

    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None

    uric_acid: Optional[float] = None
    creatinine: Optional[float] = None
    bun: Optional[float] = None

    alt: Optional[float] = None
    ast: Optional[float] = None
    hemoglobin: Optional[float] = None

    notes: Optional[str] = None


class HealthReportResponse(HealthReportBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class HealthAnalysisRequest(BaseModel):
    user_id: int
    report_id: int


# =========================
# 口味偏好相关 Schema
# =========================

class TastePreferenceBase(BaseModel):
    user_id: int
    preference_name: Optional[str] = "默认偏好"
    is_default: Optional[int] = 0

    preferred_flavors: Optional[List[str]] = Field(default_factory=list)
    disliked_foods: Optional[List[str]] = Field(default_factory=list)
    preferred_cuisines: Optional[List[str]] = Field(default_factory=list)
    allergies: Optional[List[str]] = Field(default_factory=list)

    cooking_time_limit: Optional[int] = 60
    difficulty_preference: Optional[str] = "medium"
    budget_level: Optional[str] = "medium"
    meal_count: Optional[int] = 3


class TastePreferenceCreate(TastePreferenceBase):
    pass


class TastePreferenceUpdate(BaseModel):
    preference_name: Optional[str] = None
    is_default: Optional[int] = None
    
    preferred_flavors: Optional[List[str]] = None
    disliked_foods: Optional[List[str]] = None
    preferred_cuisines: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

    cooking_time_limit: Optional[int] = None
    difficulty_preference: Optional[str] = None
    budget_level: Optional[str] = None
    meal_count: Optional[int] = None


class TastePreferenceResponse(TastePreferenceBase):
    id: int
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# =========================
# 饮食计划相关 Schema
# =========================

class MealPlanCreate(BaseModel):
    user_id: int
    title: Optional[str] = None
    plan_content: Optional[str] = None
    calories_target: Optional[int] = None
    nutrition_summary: Optional[Dict[str, Any]] = None


class WeeklyMealPlanCreate(BaseModel):
    user_id: int

    # 生成几天的计划，默认一周
    days: int = 7

    # 每天几餐
    meal_count: int = 3

    # 热量目标，兼容不同命名
    target_calories: Optional[int] = None
    calories_target: Optional[int] = None
    calorie_target: Optional[int] = None

    # 用户目标和额外要求
    health_goal: Optional[str] = None
    goal: Optional[str] = None
    requirements: Optional[str] = None

    # 可选偏好
    preferences: Optional[Dict[str, Any]] = None


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str] = None
    plan_content: Optional[str] = None
    calories_target: Optional[int] = None
    nutrition_summary: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class MealPlanGenerateRequest(BaseModel):
    user_id: int
    report_id: int
    days: int = Field(default=7, ge=1, le=14)
    meal_count: int = Field(default=3, ge=2, le=6)
    target_calories: Optional[int] = None
    requirements: Optional[str] = None
    title: Optional[str] = None


# =========================
# Agent / 问答相关 Schema
# =========================

class AgentRequest(BaseModel):
    user_id: Optional[int] = None
    message: str
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    answer: str
    data: Optional[Any] = None


class ChatRequest(BaseModel):
    user_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    response: str
    data: Optional[Any] = None