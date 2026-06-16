from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import (
    User, Version, Grade, Subject, Semester, Unit,
    KnowledgePoint, ExamPoint
)
from app.utils.auth import get_current_admin
from openpyxl import load_workbook
from io import BytesIO
from typing import List

router = APIRouter(prefix="/admin", tags=["知识考点管理"])

@router.get("/knowledge-exam-points")
def get_knowledge_exam_points(unit_id: int = None, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    query = db.query(KnowledgePoint)
    if unit_id:
        query = query.filter(KnowledgePoint.unit_id == unit_id)
    
    knowledge_points = query.all()
    result = []
    for kp in knowledge_points:
        exam_points = db.query(ExamPoint).filter(ExamPoint.knowledge_point_id == kp.id).all()
        result.append({
            "id": kp.id,
            "unit_id": kp.unit_id,
            "title": kp.title,
            "content": kp.content,
            "exam_points": [{
                "id": ep.id,
                "title": ep.title,
                "content": ep.content,
                "exam_types": ep.exam_types,
                "exam_frequency": ep.exam_frequency.value if ep.exam_frequency else None
            } for ep in exam_points]
        })
    return result

@router.post("/knowledge-exam-points")
def save_knowledge_exam_point(data: dict, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    if data.get('id'):
        kp = db.query(KnowledgePoint).filter(KnowledgePoint.id == data['id']).first()
        if kp:
            kp.title = data.get('title', kp.title)
            kp.content = data.get('content', kp.content)
            db.commit()
            
            if 'exam_points' in data:
                for ep_data in data['exam_points']:
                    if ep_data.get('id'):
                        ep = db.query(ExamPoint).filter(ExamPoint.id == ep_data['id']).first()
                        if ep:
                            ep.title = ep_data.get('title', ep.title)
                            ep.content = ep_data.get('content', ep.content)
                            ep.exam_types = ep_data.get('exam_types', ep.exam_types)
                            ep.exam_frequency = ep_data.get('exam_frequency', ep.exam_frequency)
                    else:
                        ep = ExamPoint(
                            knowledge_point_id=kp.id,
                            title=ep_data.get('title'),
                            content=ep_data.get('content'),
                            exam_types=ep_data.get('exam_types'),
                            exam_frequency=ep_data.get('exam_frequency', '常考')
                        )
                        db.add(ep)
                db.commit()
            return {"message": "更新成功"}
    
    kp = KnowledgePoint(
        unit_id=data['unit_id'],
        title=data['title'],
        content=data.get('content')
    )
    db.add(kp)
    db.commit()
    db.refresh(kp)
    
    if 'exam_points' in data:
        for ep_data in data['exam_points']:
            ep = ExamPoint(
                knowledge_point_id=kp.id,
                title=ep_data.get('title'),
                content=ep_data.get('content'),
                exam_types=ep_data.get('exam_types'),
                exam_frequency=ep_data.get('exam_frequency', '常考')
            )
            db.add(ep)
        db.commit()
    
    return {"id": kp.id, "message": "保存成功"}

@router.post("/import-knowledge-exam-points")
async def import_knowledge_exam_points(
    file: UploadFile = File(...),
    version_id: int = None,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="只支持Excel文件")
    
    contents = await file.read()
    try:
        wb = load_workbook(BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel文件解析失败: {str(e)}")
    
    imported_count = 0
    
    version = db.query(Version).filter(Version.name == "人教版").first()
    if not version:
        version = Version(name="人教版")
        db.add(version)
        db.commit()
        db.refresh(version)
    
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        
        subject_name = sheet_name.replace('小学', '').replace('初中', '').strip()
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row or not row[0]:
                continue
            
            grade_name = str(row[0]).strip() if row[0] else None
            semester_name = str(row[1]).strip() if row[1] else None
            unit_number = str(row[2]).strip() if row[2] else None
            unit_name = str(row[3]).strip() if row[3] else None
            knowledge_content = str(row[4]).strip() if row[4] else None
            exam_content = str(row[5]).strip() if row[5] else None
            exam_types = str(row[6]).strip() if row[6] else None
            exam_frequency = str(row[7]).strip() if row[7] else '常考'
            
            if not all([grade_name, semester_name, unit_number, unit_name]):
                continue
            
            grade = db.query(Grade).filter(
                Grade.version_id == version.id,
                Grade.name == grade_name
            ).first()
            if not grade:
                grade = Grade(version_id=version.id, name=grade_name)
                db.add(grade)
                db.commit()
                db.refresh(grade)
            
            subject = db.query(Subject).filter(
                Subject.grade_id == grade.id,
                Subject.name == subject_name
            ).first()
            if not subject:
                subject = Subject(grade_id=grade.id, name=subject_name)
                db.add(subject)
                db.commit()
                db.refresh(subject)
            
            semester = db.query(Semester).filter(
                Semester.subject_id == subject.id,
                Semester.name == semester_name
            ).first()
            if not semester:
                semester = Semester(subject_id=subject.id, name=semester_name)
                db.add(semester)
                db.commit()
                db.refresh(semester)
            
            unit = db.query(Unit).filter(
                Unit.semester_id == semester.id,
                Unit.name.like(f"%{unit_number}%")
            ).first()
            if not unit:
                unit = Unit(semester_id=semester.id, name=f"{unit_number} {unit_name}")
                db.add(unit)
                db.commit()
                db.refresh(unit)
            
            if knowledge_content:
                kp_title = f"{unit_name} - 知识点"
                kp = KnowledgePoint(
                    unit_id=unit.id,
                    title=kp_title,
                    content=knowledge_content
                )
                db.add(kp)
                db.commit()
                db.refresh(kp)
                
                if exam_content:
                    ep = ExamPoint(
                        knowledge_point_id=kp.id,
                        title=f"{unit_name} - 考点",
                        content=exam_content,
                        exam_types=exam_types,
                        exam_frequency=exam_frequency if exam_frequency in ['少考', '常考', '必考'] else '常考'
                    )
                    db.add(ep)
                    db.commit()
                
                imported_count += 1
    
    return {"message": f"导入成功，共导入{imported_count}条数据"}