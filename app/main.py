from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine

from app.models.user import User
from app.models.post import Post
from app.models.like import Like
from app.models.comment import Comment
from app.models.follow import Follow
from app.models.notification import Notification
from app.models.hashtag import Hashtag
from app.models.hashtag_post import PostHashtag

# routers
from app.auth.routes import router as auth_router
from app.api.posts import router as posts_router
from app.api.likes import router as likes_router
from app.api.comments import router as comments_router
from app.api.users import router as users_router
from app.api.media import router as media_router
from app.api.follows import router as follows_router
from app.api.notifications import router as notifications_router
from app.api.search import router as search_router
from app.api.hashtags import router as hashtags_router
from app.api.feed import router as feed_router
from app.chat.routes import router as chat_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend domain 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB create
Base.metadata.create_all(bind=engine)

# routers
app.include_router(auth_router, prefix="/auth")
app.include_router(posts_router)
app.include_router(chat_router)
app.include_router(likes_router)
app.include_router(comments_router)
app.include_router(users_router)
app.include_router(media_router)
app.include_router(follows_router)
app.include_router(notifications_router)
app.include_router(search_router)
app.include_router(hashtags_router)
app.include_router(feed_router)

@app.get("/")
def home():
    return {
        "message": "Backend + DB ishlayapti 🚀"
    }
