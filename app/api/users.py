from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserProfileResponse, UserProfileUpdate
from app.service.user import UserService

# 🚨 IMPORTANT: NO PREFIX HERE
router = APIRouter(tags=["users"])


# =========================
# DB SESSION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# AUTH USER
# =========================
def get_current_user_obj(
    email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# =========================
# GET CURRENT USER
# =========================
@router.get("/me", response_model=UserProfileResponse)
def get_current_profile(
    current_user: User = Depends(get_current_user_obj)
):
    return current_user


# =========================
# GET USER BY ID
# =========================
@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    user = UserService.get_user_profile(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# =========================
# UPDATE PROFILE
# =========================
@router.put("/me", response_model=UserProfileResponse)
def update_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    user = UserService.update_profile(db, current_user.id, data)
    return user
