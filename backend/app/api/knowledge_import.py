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
    skipped_count = 0
    duplicate_count = 0
    unit_knowledge_map = {}
    import_log = []
    
    version = db.query(Version).filter(Version.name == "人教版").first()
    if not version:
        version = Version(name="人教版")
        db.add(version)
        db.commit()
        db.refresh(version)
    
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        
        subject_name = sheet_name.replace('小学', '').replace('初中', '').strip()
        import_log.append(f"📄 处理Sheet: {sheet_name} -> 科目: {subject_name}")
        
        last_grade = None
        last_semester = None
        last_unit_number = None
        last_unit_name = None
        last_knowledge_content = None
        
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not row:
                continue
            
            grade_name = str(row[0]).strip() if row[0] else None
            semester_name = str(row[1]).strip() if row[1] else None
            unit_number = str(row[2]).strip() if row[2] else None
            unit_name = str(row[3]).strip() if row[3] else None
            knowledge_content = str(row[4]).strip() if row[4] else None
            exam_content = str(row[5]).strip() if row[5] else None
            exam_types = str(row[6]).strip() if row[6] else None
            exam_frequency = str(row[7]).strip() if row[7] else '常考'
            
            if grade_name:
                last_grade = grade_name
            if semester_name:
                last_semester = semester_name
            if unit_number:
                last_unit_number = unit_number
            if unit_name:
                last_unit_name = unit_name
            if knowledge_content:
                last_knowledge_content = knowledge_content
            
            if not all([last_grade, last_semester, last_unit_number, last_unit_name]):
                skipped_count += 1
                import_log.append(f"  ✗ 行{row_idx}: 缺少必要字段")
                continue
            
            if not exam_content:
                skipped_count += 1
                import_log.append(f"  ✗ 行{row_idx}: {last_unit_name} 无考点内容")
                continue
            
            grade = db.query(Grade).filter(
                Grade.version_id == version.id,
                Grade.name == last_grade
            ).first()
            if not grade:
                grade = Grade(version_id=version.id, name=last_grade)
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
                Semester.name == last_semester
            ).first()
            if not semester:
                semester = Semester(subject_id=subject.id, name=last_semester)
                db.add(semester)
                db.commit()
                db.refresh(semester)
            
            unit = db.query(Unit).filter(
                Unit.semester_id == semester.id,
                Unit.name.like(f"%{last_unit_number}%")
            ).first()
            if not unit:
                unit = Unit(semester_id=semester.id, name=f"{last_unit_number} {last_unit_name}")
                db.add(unit)
                db.commit()
                db.refresh(unit)
            
            unit_key = f"{last_grade}-{subject_name}-{last_semester}-{last_unit_number}"
            
            if unit_key not in unit_knowledge_map:
                kp = db.query(KnowledgePoint).filter(
                    KnowledgePoint.unit_id == unit.id
                ).first()
                
                if not kp:
                    kp_content = last_knowledge_content or ""
                    kp = KnowledgePoint(
                        unit_id=unit.id,
                        title=f"{last_unit_name} - 知识点",
                        content=kp_content
                    )
                    db.add(kp)
                    db.commit()
                    db.refresh(kp)
                    import_log.append(f"  ✓ 创建知识点: {last_unit_name}")
                
                unit_knowledge_map[unit_key] = kp
            
            kp = unit_knowledge_map[unit_key]
            
            if last_knowledge_content and kp.content != last_knowledge_content:
                kp.content = last_knowledge_content
                db.commit()
            
            if exam_content:
                existing_ep = db.query(ExamPoint).filter(
                    ExamPoint.knowledge_point_id == kp.id,
                    ExamPoint.content == exam_content
                ).first()
                
                if not existing_ep:
                    exam_title = exam_content.split('\n')[0][:50] if '\n' in exam_content else exam_content[:50]
                    ep = ExamPoint(
                        knowledge_point_id=kp.id,
                        title=exam_title,
                        content=exam_content,
                        exam_types=exam_types,
                        exam_frequency=exam_frequency if exam_frequency in ['少考', '常考', '必考', '必考重点'] else '常考'
                    )
                    db.add(ep)
                    db.commit()
                    imported_count += 1
                    import_log.append(f"  ✓ 行{row_idx}: {exam_title[:30]} ({exam_frequency})")
                else:
                    duplicate_count += 1
                    import_log.append(f"  - 行{row_idx}: 重复考点")
    
    return {
        "message": f"导入完成",
        "imported": imported_count,
        "skipped": skipped_count,
        "duplicate": duplicate_count,
        "log": import_log[:50]
    }

@router.post("/clean-duplicate-exam-points")
def clean_duplicate_exam_points(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    all_kps = db.query(KnowledgePoint).all()
    deleted_count = 0
    
    for kp in all_kps:
        exam_points = db.query(ExamPoint).filter(ExamPoint.knowledge_point_id == kp.id).all()
        
        seen_contents = set()
        for ep in exam_points:
            if ep.content in seen_contents:
                db.delete(ep)
                deleted_count += 1
            else:
                seen_contents.add(ep.content)
    
    db.commit()
    return {"message": f"清理完成，删除了{deleted_count}条重复考点"}

@router.delete("/unit-knowledge/{unit_id}")
def delete_unit_knowledge(
    unit_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    kps = db.query(KnowledgePoint).filter(KnowledgePoint.unit_id == unit_id).all()
    deleted_count = 0
    for kp in kps:
        db.query(ExamPoint).filter(ExamPoint.knowledge_point_id == kp.id).delete()
        db.delete(kp)
        deleted_count += 1
    db.commit()
    return {"message": f"删除成功，共删除{deleted_count}个知识点及其考点"}
