from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # recipient
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # who triggered it
    notification_type = Column(String, nullable=False)  # like, comment, follow
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", foreign_keys=[user_id], backref="notifications")
    actor = relationship("User", foreign_keys=[actor_id])
    post = relationship("Post", backref="notifications")
    comment = relationship("Comment")
