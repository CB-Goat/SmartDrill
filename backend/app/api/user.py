from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Recharge, Order
from app.schemas.schemas import RechargeRequest, OrderResponse
from app.utils.auth import get_current_user
from typing import List

router = APIRouter(prefix="/user", tags=["用户"])

@router.get("/info")
def get_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "phone": current_user.phone,
        "points": current_user.points,
        "role": current_user.role.value
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