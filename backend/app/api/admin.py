from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import (
    User, Recharge, Order, Version, Grade, Subject, Semester, Unit,
    KnowledgePoint, ExamPoint, QuestionType, Difficulty, Question
)
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

@router.get("/versions")
def get_versions(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Version).all()

@router.post("/versions")
def save_version(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    try:
        v = Version(name=data.get('name', ''))
        db.add(v)
        db.commit()
        db.refresh(v)
        return {"id": v.id, "name": v.name}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建版本失败: {str(e)}")

@router.delete("/versions/{id}")
def delete_version(id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    v = db.query(Version).filter(Version.id == id).first()
    if not v:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(v)
    db.commit()
    return {"message": "删除成功"}

@router.get("/grades")
def get_grades(version_id: int = None, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Grade)
    if version_id:
        query = query.filter(Grade.version_id == version_id)
    return query.all()

@router.post("/grades")
def save_grade(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    g = Grade(**data)
    db.add(g)
    db.commit()
    db.refresh(g)
    return {"id": g.id, "name": g.name, "version_id": g.version_id}

@router.delete("/grades/{id}")
def delete_grade(id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    g = db.query(Grade).filter(Grade.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(g)
    db.commit()
    return {"message": "删除成功"}

@router.get("/subjects")
def get_subjects(grade_id: int = None, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Subject)
    if grade_id:
        query = query.filter(Subject.grade_id == grade_id)
    return query.all()

@router.post("/subjects")
def save_subject(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = Subject(**data)
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "name": s.name, "grade_id": s.grade_id}

@router.delete("/subjects/{id}")
def delete_subject(id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.query(Subject).filter(Subject.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(s)
    db.commit()
    return {"message": "删除成功"}

@router.get("/semesters")
def get_semesters(subject_id: int = None, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Semester)
    if subject_id:
        query = query.filter(Semester.subject_id == subject_id)
    return query.all()

@router.post("/semesters")
def save_semester(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = Semester(**data)
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "name": s.name, "subject_id": s.subject_id}

@router.delete("/semesters/{id}")
def delete_semester(id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.query(Semester).filter(Semester.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(s)
    db.commit()
    return {"message": "删除成功"}

@router.get("/units")
def get_units(semester_id: int = None, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Unit)
    if semester_id:
        query = query.filter(Unit.semester_id == semester_id)
    return query.all()

@router.post("/units")
def save_unit(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    u = Unit(**data)
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"id": u.id, "name": u.name, "semester_id": u.semester_id}

@router.delete("/units/{id}")
def delete_unit(id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    u = db.query(Unit).filter(Unit.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="记录不存在")
    db.delete(u)
    db.commit()
    return {"message": "删除成功"}

@router.get("/knowledge")
def get_knowledge(unit_id: int = None, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(KnowledgePoint)
    if unit_id:
        query = query.filter(KnowledgePoint.unit_id == unit_id)
    return query.all()

@router.post("/knowledge")
def save_knowledge(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    if data.get('id'):
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == data['id']).first()
        if kp:
            for key, value in data.items():
                setattr(kp, key, value)
            db.commit()
            return {"message": "更新成功"}
    kp = KnowledgePoint(**{k: v for k, v in data.items() if k != 'id'})
    db.add(kp)
    db.commit()
    db.refresh(kp)
    return {"id": kp.id, "message": "保存成功"}

@router.get("/exam-points")
def get_exam_points(knowledge_point_id: int = None, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(ExamPoint)
    if knowledge_point_id:
        query = query.filter(ExamPoint.knowledge_point_id == knowledge_point_id)
    return query.all()

@router.post("/exam-points")
def save_exam_point(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    if data.get('id'):
        ep = db.query(ExamPoint).filter(ExamPoint.id == data['id']).first()
        if ep:
            for key, value in data.items():
                setattr(ep, key, value)
            db.commit()
            return {"message": "更新成功"}
    ep = ExamPoint(**{k: v for k, v in data.items() if k != 'id'})
    db.add(ep)
    db.commit()
    db.refresh(ep)
    return {"id": ep.id, "message": "保存成功"}

@router.get("/question-types")
def get_question_types(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(QuestionType).all()

@router.get("/difficulties")
def get_difficulties(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Difficulty).all()

@router.get("/questions")
def get_questions(unit_id: int = None, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(Question)
    if unit_id:
        query = query.filter(Question.unit_id == unit_id)
    questions = query.all()
    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "content": q.content,
            "answer": q.answer,
            "analysis": q.analysis,
            "question_type": q.question_type_obj.name if q.question_type_obj else None,
            "difficulty": q.difficulty_obj.name if q.difficulty_obj else None,
            "exam_point_title": q.exam_point.title if q.exam_point else None,
            "question_type_id": q.question_type_id,
            "difficulty_id": q.difficulty_id,
            "unit_id": q.unit_id,
            "knowledge_point_id": q.knowledge_point_id,
            "exam_point_id": q.exam_point_id
        })
    return result

@router.post("/questions")
def save_question(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    if data.get('id'):
        q = db.query(Question).filter(Question.id == data['id']).first()
        if q:
            for key, value in data.items():
                setattr(q, key, value)
            db.commit()
            return {"message": "更新成功"}
    q = Question(**{k: v for k, v in data.items() if k != 'id'})
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"id": q.id, "message": "保存成功"}