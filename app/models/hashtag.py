from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.base import Base


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
