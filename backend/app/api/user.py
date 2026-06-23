from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Recharge, Order
from app.schemas.schemas import RechargeRequest, OrderResponse
from app.utils.auth import get_current_user, hash_password, verify_password
from typing import List

router = APIRouter(prefix="/user", tags=["用户"])

@router.get("/info")
def get_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "phone": current_user.phone,
        "points": current_user.points
    }

@router.post("/recharge")
def recharge(data: RechargeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    points = data.amount * 100
    current_user.points += points
    
    recharge_record = Recharge(
        user_id=current_user.id,
        amount=data.amount,
        points=points
    )
    db.add(recharge_record)
    db.commit()
    return {"message": "充值成功", "points": points}

@router.get("/orders", response_model=List[OrderResponse])
def get_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()
    return orders

@router.post("/update-phone")
def update_phone(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    phone = data.get('phone')
    if not phone:
        raise HTTPException(status_code=400, detail="手机号不能为空")
    
    current_user.phone = phone
    db.commit()
    return {"message": "修改成功"}

@router.post("/update-password")
def update_password(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        raise HTTPException(status_code=400, detail="密码不能为空")
    
    if not verify_password(old_password, current_user.password):
        raise HTTPException(status_code=400, detail="旧密码错误")
    
    current_user.password = hash_password(new_password)
    db.commit()
    return {"message": "修改成功"}