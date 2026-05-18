import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nexora"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for now, can be shorter
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_YAlZv5QE0Mzb@ep-calm-scene-aq4w4ju9-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
    
    # Uploadcare
    UPLOADCARE_PUBLIC_KEY: str = os.getenv("UPLOADCARE_PUBLIC_KEY", "")
    UPLOADCARE_PRIVATE_KEY: str = os.getenv("UPLOADCARE_PRIVATE_KEY", "")
    UPLOADCARE_API_BASE_URL: str = "https://api.uploadcare.com"
    
    # Media Constraints
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    MAX_VIDEO_SIZE: int = 500 * 1024 * 1024  # 500MB
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]


settings = Settings()
