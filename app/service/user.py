from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserProfileUpdate
from fastapi import HTTPException


class UserService:
    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    def update_profile(db: Session, user_id: int, data: UserProfileUpdate) -> User:
        user = UserService.get_user_profile(db, user_id)
        
        if data.username is not None:
            # Check if username already exists
            existing = db.query(User).filter(
                User.username == data.username,
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = data.username
        
        if data.bio is not None:
            user.bio = data.bio
        
        if data.profile_pic_url is not None:
            user.profile_pic_url = data.profile_pic_url
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()
