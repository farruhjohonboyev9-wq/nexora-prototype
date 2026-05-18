from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
