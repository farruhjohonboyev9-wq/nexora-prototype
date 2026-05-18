from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Follow(Base):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint('follower_id', 'following_id', name='unique_follower_following'),)

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    follower = relationship("User", foreign_keys=[follower_id], backref="following_rel")
    following = relationship("User", foreign_keys=[following_id], backref="followers_rel")
