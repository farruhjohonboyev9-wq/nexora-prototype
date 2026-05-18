from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base


class PostHashtag(Base):
    __tablename__ = "post_hashtags"
    __table_args__ = (UniqueConstraint('post_id', 'hashtag_id', name='unique_post_hashtag'),)

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    hashtag_id = Column(Integer, ForeignKey("hashtags.id"), nullable=False)
    
    post = relationship("Post", backref="hashtags_rel")
    hashtag = relationship("Hashtag", backref="posts_rel")
