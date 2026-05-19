from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine

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

app = FastAPI(title="Nexora API", version="1.0.0")

# 🔥 TEMP CORS FIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(posts_router, prefix="/posts", tags=["Posts"])
app.include_router(likes_router, prefix="/likes", tags=["Likes"])
app.include_router(comments_router, prefix="/comments", tags=["Comments"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(media_router, prefix="/media", tags=["Media"])
app.include_router(follows_router, prefix="/follows", tags=["Follows"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(search_router, prefix="/search", tags=["Search"])
app.include_router(hashtags_router, prefix="/hashtags", tags=["Hashtags"])
app.include_router(feed_router, prefix="/feed", tags=["Feed"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

@app.get("/")
def home():
    return {"message": "Backend ishlayapti 🚀"}
