from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserLogin, Token, UserResponse
from app.utils.auth import verify_password, get_password_hash, create_access_token
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["认证"])

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    user = User(
        username=user_data.username,
        password=get_password_hash(user_data.password),
        phone=user_data.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "注册成功"}

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": user.username, "type": "user"})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(id=user.id, username=user.username, phone=user.phone, points=user.points)
    }