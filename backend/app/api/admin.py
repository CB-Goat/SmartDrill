from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Recharge, Order, KnowledgePoint, Question
from app.utils.auth import get_current_admin
from typing import List

router = APIRouter(prefix="/admin", tags=["管理"])

@router.get("/users")
def get_users(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "phone": u.phone, "points": u.points, "role": u.role.value} for u in users]

@router.get("/recharges")
def get_recharges(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    recharges = db.query(Recharge).order_by(Recharge.created_at.desc()).all()
    return [{"id": r.id, "username": r.user.username, "amount": r.amount, "points": r.points, "created_at": r.created_at} for r in recharges]

@router.get("/orders")
def get_orders(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return [{"id": o.id, "username": o.user.username, "title": o.title, "points": o.points, "created_at": o.created_at} for o in orders]

@router.get("/knowledge")
def get_knowledge(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(KnowledgePoint).all()

@router.post("/knowledge")
def save_knowledge(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    kp = KnowledgePoint(**data)
    db.add(kp)
    db.commit()
    return {"message": "保存成功"}

@router.get("/questions")
def get_questions(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Question).all()

@router.post("/questions")
def save_question(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    q = Question(**data)
    db.add(q)
    db.commit()
    return {"message": "保存成功"}