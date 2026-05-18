from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationDetailResponse, UnreadCountResponse
from app.service.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_obj(email: str = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("", response_model=list[NotificationDetailResponse])
def get_notifications(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    notifications = NotificationService.get_user_notifications(db, current_user.id, skip, limit)
    return [
        {
            **n.__dict__,
            "actor": n.actor
        }
        for n in notifications
    ]


@router.put("/{notification_id}/read")
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification = NotificationService.mark_as_read(db, notification_id, current_user.id)
    return {"id": notification.id, "is_read": notification.is_read}


@router.put("/read-all")
def mark_all_as_read(
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    NotificationService.mark_all_as_read(db, current_user.id)
    return {"message": "All notifications marked as read"}


@router.get("/unread/count", response_model=UnreadCountResponse)
def get_unread_count(
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    count = NotificationService.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user_obj),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    NotificationService.delete_notification(db, notification_id, current_user.id)
    return {"message": "Notification deleted"}
