from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Order, KnowledgePoint, Question
from app.schemas.schemas import ReviewRequest, PracticeRequest
from app.utils.auth import get_current_user
from app.services.document import generate_review_document, generate_practice_document
import os

router = APIRouter(prefix="/materials", tags=["资料"])

@router.post("/review")
def get_review_materials(data: ReviewRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.points < 10:
        raise HTTPException(status_code=400, detail="积分不足")
    
    knowledge_points = db.query(KnowledgePoint).filter(KnowledgePoint.unit_id == data.unitId).all()
    
    if not knowledge_points:
        raise HTTPException(status_code=404, detail="未找到知识点")
    
    current_user.points -= 10
    
    file_path = generate_review_document(knowledge_points, current_user.id)
    
    order = Order(
        user_id=current_user.id,
        title=f"复习资料-单元{data.unitId}",
        order_type="review",
        points=10,
        file_path=file_path
    )
    db.add(order)
    db.commit()
    
    return {"message": "订单创建成功", "order_id": order.id}

@router.post("/practice")
def get_practice_questions(data: PracticeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.points < data.questionCount:
        raise HTTPException(status_code=400, detail="积分不足")
    
    questions = db.query(Question).filter(
        Question.unit_id == data.unitId,
        Question.difficulty == data.difficulty,
        Question.exam_type == data.examType
    ).limit(data.questionCount).all()
    
    if not questions:
        raise HTTPException(status_code=404, detail="未找到符合条件的题目")
    
    current_user.points -= data.questionCount
    
    file_path = generate_practice_document(questions, current_user.id)
    
    order = Order(
        user_id=current_user.id,
        title=f"练习题-{data.questionCount}题",
        order_type="practice",
        points=data.questionCount,
        file_path=file_path
    )
    db.add(order)
    db.commit()
    
    return {"message": "订单创建成功", "order_id": order.id}

@router.get("/orders/{order_id}/download")
def download_order(order_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    if not order.file_path or not os.path.exists(order.file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(order.file_path, filename=f"order_{order_id}.docx", media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")