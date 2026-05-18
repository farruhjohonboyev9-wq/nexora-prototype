from .jwt import create_token
from .security import verify_password

@router.post("/login")
def login(data: LoginSchema):
    db = SessionLocal()

    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }