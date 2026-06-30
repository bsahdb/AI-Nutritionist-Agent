from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import TastePreference
from core.schemas import StandardResponse, TastePreferenceCreate, TastePreferenceUpdate

router = APIRouter(
    prefix="/preferences",
    tags=["preferences"]
)


def serialize_preference(pref: TastePreference):
    return {
        "id": pref.id,
        "user_id": pref.user_id,
        "preference_name": getattr(pref, "preference_name", None) or "默认偏好",
        "is_default": getattr(pref, "is_default", 0) or 0,
        "preferred_flavors": pref.preferred_flavors or [],
        "disliked_foods": pref.disliked_foods or [],
        "preferred_cuisines": pref.preferred_cuisines or [],
        "allergies": pref.allergies or [],
        "cooking_time_limit": pref.cooking_time_limit,
        "difficulty_preference": pref.difficulty_preference,
        "budget_level": pref.budget_level,
        "meal_count": pref.meal_count,
        "updated_at": pref.updated_at.isoformat() if pref.updated_at else None,
    }


def get_default_preference(db: Session, user_id: int):
    pref = db.query(TastePreference).filter(
        TastePreference.user_id == user_id,
        TastePreference.is_default == 1
    ).first()

    if pref:
        return pref

    return db.query(TastePreference).filter(
        TastePreference.user_id == user_id
    ).order_by(TastePreference.updated_at.desc()).first()


@router.get("/", response_model=StandardResponse)
def list_preferences(db: Session = Depends(get_db)):
    preferences = db.query(TastePreference).order_by(
        TastePreference.user_id.asc(),
        TastePreference.is_default.desc(),
        TastePreference.id.desc()
    ).all()

    return StandardResponse(
        success=True,
        message="获取口味偏好列表成功",
        data=[serialize_preference(pref) for pref in preferences]
    )


@router.get("/user/{user_id}", response_model=StandardResponse)
def list_preferences_by_user(user_id: int, db: Session = Depends(get_db)):
    preferences = db.query(TastePreference).filter(
        TastePreference.user_id == user_id
    ).order_by(
        TastePreference.is_default.desc(),
        TastePreference.id.desc()
    ).all()

    return StandardResponse(
        success=True,
        message="获取用户口味偏好列表成功",
        data=[serialize_preference(pref) for pref in preferences]
    )


@router.get("/detail/{pref_id}", response_model=StandardResponse)
def get_preference_detail(pref_id: int, db: Session = Depends(get_db)):
    pref = db.query(TastePreference).filter(TastePreference.id == pref_id).first()

    if not pref:
        raise HTTPException(status_code=404, detail="口味偏好不存在")

    return StandardResponse(
        success=True,
        message="获取口味偏好详情成功",
        data=serialize_preference(pref)
    )


@router.post("/", response_model=StandardResponse)
def create_preference(payload: TastePreferenceCreate, db: Session = Depends(get_db)):
    existing_count = db.query(TastePreference).filter(
        TastePreference.user_id == payload.user_id
    ).count()

    data = payload.model_dump()

    if not data.get("preference_name"):
        data["preference_name"] = "默认偏好" if existing_count == 0 else f"偏好{existing_count + 1}"

    # 如果是第一条偏好，自动设为默认
    if existing_count == 0:
        data["is_default"] = 1

    # 如果新建时指定为默认，则清除其他默认
    if data.get("is_default") == 1:
        db.query(TastePreference).filter(
            TastePreference.user_id == payload.user_id
        ).update({"is_default": 0})

    pref = TastePreference(**data)

    db.add(pref)
    db.commit()
    db.refresh(pref)

    return StandardResponse(
        success=True,
        message="口味偏好创建成功",
        data=serialize_preference(pref)
    )


@router.put("/detail/{pref_id}", response_model=StandardResponse)
def update_preference_by_id(
    pref_id: int,
    payload: TastePreferenceUpdate,
    db: Session = Depends(get_db)
):
    pref = db.query(TastePreference).filter(TastePreference.id == pref_id).first()

    if not pref:
        raise HTTPException(status_code=404, detail="口味偏好不存在")

    update_data = payload.model_dump(exclude_unset=True)

    if update_data.get("is_default") == 1:
        db.query(TastePreference).filter(
            TastePreference.user_id == pref.user_id,
            TastePreference.id != pref.id
        ).update({"is_default": 0})

    for key, value in update_data.items():
        setattr(pref, key, value)

    db.commit()
    db.refresh(pref)

    return StandardResponse(
        success=True,
        message="口味偏好更新成功",
        data=serialize_preference(pref)
    )


@router.delete("/detail/{pref_id}", response_model=StandardResponse)
def delete_preference(pref_id: int, db: Session = Depends(get_db)):
    pref = db.query(TastePreference).filter(TastePreference.id == pref_id).first()

    if not pref:
        raise HTTPException(status_code=404, detail="口味偏好不存在")

    user_id = pref.user_id
    was_default = pref.is_default == 1

    db.delete(pref)
    db.commit()

    # 如果删除的是默认偏好，则把该用户剩余最新一条设为默认
    if was_default:
        latest = db.query(TastePreference).filter(
            TastePreference.user_id == user_id
        ).order_by(TastePreference.id.desc()).first()

        if latest:
            latest.is_default = 1
            db.commit()

    return StandardResponse(
        success=True,
        message="口味偏好删除成功",
        data={"id": pref_id}
    )


@router.put("/default/{pref_id}", response_model=StandardResponse)
def set_default_preference(pref_id: int, db: Session = Depends(get_db)):
    pref = db.query(TastePreference).filter(TastePreference.id == pref_id).first()

    if not pref:
        raise HTTPException(status_code=404, detail="口味偏好不存在")

    db.query(TastePreference).filter(
        TastePreference.user_id == pref.user_id
    ).update({"is_default": 0})

    pref.is_default = 1

    db.commit()
    db.refresh(pref)

    return StandardResponse(
        success=True,
        message="默认口味偏好设置成功",
        data=serialize_preference(pref)
    )


# 兼容旧接口：获取某用户默认偏好
@router.get("/{user_id}", response_model=StandardResponse)
def get_preference_by_user(user_id: int, db: Session = Depends(get_db)):
    pref = get_default_preference(db, user_id)

    if not pref:
        raise HTTPException(status_code=404, detail="该用户暂无口味偏好")

    return StandardResponse(
        success=True,
        message="获取用户默认口味偏好成功",
        data=serialize_preference(pref)
    )


# 兼容旧接口：更新某用户默认偏好
@router.put("/{user_id}", response_model=StandardResponse)
def update_default_preference_by_user(
    user_id: int,
    payload: TastePreferenceUpdate,
    db: Session = Depends(get_db)
):
    pref = get_default_preference(db, user_id)

    if not pref:
        raise HTTPException(status_code=404, detail="该用户暂无口味偏好")

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(pref, key, value)

    db.commit()
    db.refresh(pref)

    return StandardResponse(
        success=True,
        message="默认口味偏好更新成功",
        data=serialize_preference(pref)
    )