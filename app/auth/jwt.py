from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"

def create_token(data: dict, expire_minutes: int = 60):
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    payload.update({"exp": expire})

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
