import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import User
from core.schemas import StandardResponse, UserCreate, UserUpdate


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


def hash_password(password: str | None) -> str:
    raw = password or "123456"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "gender": user.gender,
        "age": user.age,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "bmi": user.bmi,
        "health_goals": user.health_goals or [],
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.get("/", response_model=StandardResponse)
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id.asc()).all()

    return StandardResponse(
        success=True,
        message="获取用户列表成功",
        data=[serialize_user(user) for user in users]
    )


@router.get("/{user_id}", response_model=StandardResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return StandardResponse(
        success=True,
        message="获取用户成功",
        data=serialize_user(user)
    )


@router.post("/", response_model=StandardResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()

    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    password_hash = payload.password_hash or hash_password(payload.password)

    user = User(
        username=payload.username,
        password_hash=password_hash,
        gender=payload.gender,
        age=payload.age,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        health_goals=payload.health_goals or []
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return StandardResponse(
        success=True,
        message="用户创建成功",
        data=serialize_user(user)
    )


@router.put("/{user_id}", response_model=StandardResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return StandardResponse(
        success=True,
        message="用户更新成功",
        data=serialize_user(user)
    )


@router.delete("/{user_id}", response_model=StandardResponse)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.id == 1:
        raise HTTPException(status_code=400, detail="演示用户不建议删除")

    db.delete(user)
    db.commit()

    return StandardResponse(
        success=True,
        message="用户删除成功",
        data={"id": user_id}
    )