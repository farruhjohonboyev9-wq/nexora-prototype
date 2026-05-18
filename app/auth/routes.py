from fastapi import APIRouter, HTTPException
from app.db.session import SessionLocal
from app.models.user import User
from .schemas import RegisterSchema, LoginSchema
from .securty import hash_password, verify_password
from .jwt import create_token

router = APIRouter()


@router.post("/register")
def register(data: RegisterSchema):
    db = SessionLocal()

    try:
        # check existing user
        user = db.query(User).filter(User.email == data.email).first()
        if user:
            raise HTTPException(status_code=400, detail="User already exists")

        # create user
        new_user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created",
            "user_id": new_user.id
        }

    finally:
        db.close()


@router.post("/login")
def login(data: LoginSchema):
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == data.email).first()

        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_token({"sub": user.email})

        return {
            "access_token": token,
            "token_type": "bearer"
        }
    
    finally:
        db.close()