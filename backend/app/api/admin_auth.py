from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import AdminUser
from app.utils.auth import verify_password, get_password_hash, create_access_token, get_current_admin

router = APIRouter(prefix="/admin/auth", tags=["管理员认证"])

@router.post("/login")
def admin_login(data: dict, db: Session = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin or not verify_password(password, admin.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": admin.username, "type": "admin"})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": admin.id, "username": admin.username}
    }

@router.get("/info")
def get_admin_info(current_admin: AdminUser = Depends(get_current_admin)):
    return {"id": current_admin.id, "username": current_admin.username}