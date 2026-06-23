from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Grade, Subject, Semester, Unit
from app.utils.auth import get_current_user

router = APIRouter(prefix="/subjects", tags=["学科"])

@router.get("/grades")
def get_grades(db: Session = Depends(get_db)):
    grades = db.query(Grade).all()
    return [{
        "id": g.id,
        "name": g.name,
        "version_id": g.version_id,
        "version_name": g.version.name if g.version else ""
    } for g in grades]

@router.get("/")
def get_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()

@router.get("/{subject_id}/semesters")
def get_semesters(subject_id: int, db: Session = Depends(get_db)):
    return db.query(Semester).filter(Semester.subject_id == subject_id).all()

@router.get("/{subject_id}/semesters/{semester_id}/units")
def get_units(subject_id: int, semester_id: int, db: Session = Depends(get_db)):
    return db.query(Unit).filter(Unit.semester_id == semester_id).all()