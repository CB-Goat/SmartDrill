from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Grade, Subject, Semester, Unit, KnowledgePoint, ExamPoint, Order
from app.utils.auth import get_current_user
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO
from urllib.parse import quote

router = APIRouter(prefix="/user", tags=["用户首页"])

GRADE_ORDER = ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级', '初一', '七年级', '初二', '八年级', '初三', '九年级']

def calculate_current_grade(db, user):
    if not user.child_grade_id or not user.child_grade_set_at:
        return None, 0, '上册'
    
    set_grade = db.query(Grade).filter(Grade.id == user.child_grade_id).first()
    if not set_grade:
        return None, 0, '上册'
    
    from datetime import datetime
    days_passed = (datetime.now() - user.child_grade_set_at).days
    months_passed = days_passed / 30
    
    try:
        set_idx = GRADE_ORDER.index(set_grade.name)
    except ValueError:
        current_month = datetime.now().month
        semester = '下册' if current_month >= 2 and current_month <= 7 else '上册'
        return set_grade, months_passed % 12, semester
    
    grade_offset = int(months_passed / 12)
    current_idx = min(set_idx + grade_offset, len(GRADE_ORDER) - 1)
    
    current_grade = db.query(Grade).filter(
        Grade.version_id == set_grade.version_id,
        Grade.name == GRADE_ORDER[current_idx]
    ).first()
    
    months_in_grade = months_passed % 12 if current_idx < len(GRADE_ORDER) - 1 else 12
    
    current_month = datetime.now().month
    semester = '下册' if current_month >= 2 and current_month <= 7 else '上册'
    
    return (current_grade or set_grade), months_in_grade, semester

def calculate_current_unit_number(current_month, semester):
    if semester == '上册':
        if current_month >= 9:
            return current_month - 8
        else:
            return current_month + 4
    else:
        if current_month >= 2:
            return current_month - 1
        else:
            return 6

def set_run_shading(run, color='D9D9D9'):
    rPr = run._r.get_or_add_rPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color)
    rPr.append(shd)

def format_content(doc, content):
    if not content:
        return
    
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        if line.startswith('【') and '】' in line:
            end_idx = line.index('】')
            title_text = line[:end_idx + 1]
            rest_text = line[end_idx + 1:].strip()
            
            p = doc.add_paragraph()
            run = p.add_run(title_text)
            run.font.bold = True
            run.font.size = Pt(12)
            
            if rest_text:
                p2 = doc.add_paragraph()
                p2.paragraph_format.first_line_indent = Pt(24)
                p2.add_run(rest_text)
            
            i += 1
        elif '：' in line or ':' in line:
            colon_char = '：' if '：' in line else ':'
            colon_idx = line.index(colon_char)
            key_text = line[:colon_idx].strip()
            value_text = line[colon_idx + 1:].strip()
            
            p = doc.add_paragraph()
            key_run = p.add_run(key_text + colon_char)
            key_run.font.bold = True
            set_run_shading(key_run)
            if value_text:
                p.add_run(value_text)
            i += 1
        else:
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Pt(24)
            p.add_run(line)
            i += 1

@router.get("/home-data")
def get_home_data(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    
    current_grade, months_in_grade, current_semester = calculate_current_grade(db, user)
    
    if not current_grade:
        return {"subjects": [], "grade_name": None, "semester": None}
    
    subjects = db.query(Subject).filter(Subject.grade_id == current_grade.id).all()
    current_month = datetime.now().month
    current_unit_num = calculate_current_unit_number(current_month, current_semester)
    
    result = []
    for subject in subjects:
        semesters = db.query(Semester).filter(Semester.subject_id == subject.id).all()
        if not semesters:
            continue
        
        target_semester = None
        for sem in semesters:
            if (current_semester == '上册' and ('上' in sem.name or '一' in sem.name)) or \
               (current_semester == '下册' and ('下' in sem.name or '二' in sem.name)):
                target_semester = sem
                break
        
        if not target_semester:
            for sem in semesters:
                target_semester = sem
                break
        
        if not target_semester:
            continue
        
        all_units = db.query(Unit).filter(
            Unit.semester_id == target_semester.id
        ).order_by(Unit.unit_number).all()
        
        if not all_units:
            continue
        
        nearby_units = []
        for unit in all_units:
            unit_num = int(unit.unit_number) if isinstance(unit.unit_number, str) else unit.unit_number
            if abs(unit_num - current_unit_num) <= 1:
                has_knowledge = db.query(KnowledgePoint).filter(KnowledgePoint.unit_id == unit.id).first() is not None
                has_exam = db.query(ExamPoint).filter(ExamPoint.unit_id == unit.id).first() is not None
                downloaded = db.query(Order).filter(
                    Order.user_id == user.id,
                    Order.title.like(f"%{unit.name}%")
                ).first() is not None
                nearby_units.append({
                    "id": unit.id,
                    "name": unit.name,
                    "unit_number": unit.unit_number,
                    "semester_name": target_semester.name,
                    "has_knowledge": has_knowledge,
                    "has_exam": has_exam,
                    "downloaded": downloaded
                })
        
        if len(nearby_units) < 3:
            for unit in reversed(all_units):
                if unit.id not in [u['id'] for u in nearby_units]:
                    has_knowledge = db.query(KnowledgePoint).filter(KnowledgePoint.unit_id == unit.id).first() is not None
                    has_exam = db.query(ExamPoint).filter(ExamPoint.unit_id == unit.id).first() is not None
                    downloaded = db.query(Order).filter(
                        Order.user_id == user.id,
                        Order.title.like(f"%{unit.name}%")
                    ).first() is not None
                    nearby_units.append({
                        "id": unit.id,
                        "name": unit.name,
                        "unit_number": unit.unit_number,
                        "semester_name": target_semester.name,
                        "has_knowledge": has_knowledge,
                        "has_exam": has_exam,
                        "downloaded": downloaded
                    })
                    if len(nearby_units) >= 3:
                        break
        
        nearby_units = sorted(nearby_units, key=lambda u: int(u['unit_number']) if isinstance(u['unit_number'], str) else u['unit_number'])
        
        if nearby_units:
            result.append({
                "subject_id": subject.id,
                "subject_name": subject.name,
                "grade_name": current_grade.name,
                "semester": current_semester,
                "units": nearby_units[:3]
            })
    
    return {"subjects": result, "grade_name": current_grade.name, "semester": current_semester}

@router.get("/unit-word/{unit_id}")
def get_unit_word(
    unit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="单元不存在")
    
    semester = db.query(Semester).filter(Semester.id == unit.semester_id).first()
    subject = db.query(Subject).filter(Subject.id == semester.subject_id).first() if semester else None
    grade = db.query(Grade).filter(Grade.id == subject.grade_id).first() if subject else None
    
    knowledge = db.query(KnowledgePoint).filter(KnowledgePoint.unit_id == unit_id).first()
    exam_points = db.query(ExamPoint).filter(ExamPoint.unit_id == unit_id).all()
    
    doc = Document()
    
    style = doc.styles['Normal']
    style.font.name = '宋体'
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    
    title_text = f"{grade.name if grade else ''} {subject.name if subject else ''} {semester.name if semester else ''} - {unit.name}"
    
    title = doc.add_paragraph()
    title_run = title.add_run(title_text)
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.name = '宋体'
    title_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle_run = subtitle.add_run("知识点")
    subtitle_run.font.size = Pt(16)
    subtitle_run.font.bold = True
    subtitle_run.font.color.rgb = RGBColor(0, 102, 204)
    subtitle_run.font.name = '宋体'
    subtitle_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if knowledge and knowledge.content:
        format_content(doc, knowledge.content)
    else:
        p = doc.add_paragraph()
        run = p.add_run("暂无知识点内容")
        run.font.color.rgb = RGBColor(153, 153, 153)
    
    doc.add_page_break()
    
    subtitle2 = doc.add_paragraph()
    subtitle2_run = subtitle2.add_run("考点")
    subtitle2_run.font.size = Pt(16)
    subtitle2_run.font.bold = True
    subtitle2_run.font.color.rgb = RGBColor(0, 102, 204)
    subtitle2_run.font.name = '宋体'
    subtitle2_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
    subtitle2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if exam_points:
        for idx, ep in enumerate(exam_points, 1):
            p = doc.add_paragraph()
            
            tab_stops = p.paragraph_format.tab_stops
            tab_stops.add_tab_stop(Inches(2.5), WD_TAB_ALIGNMENT.CENTER)
            tab_stops.add_tab_stop(Inches(5.5), WD_TAB_ALIGNMENT.RIGHT)
            
            title_run = p.add_run(f"{idx}. {ep.title}")
            title_run.font.size = Pt(14)
            title_run.font.bold = True
            title_run.font.name = '宋体'
            title_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            
            p.add_run('\t')
            
            if ep.exam_types:
                types_run = p.add_run(f"{{{ep.exam_types}}}")
                types_run.font.size = Pt(12)
                types_run.font.name = '宋体'
                types_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                types_run.font.color.rgb = RGBColor(255, 105, 180)
            
            p.add_run('\t')
            
            if ep.exam_frequency:
                freq_text = ep.exam_frequency.value
                freq_run = p.add_run(f"[{freq_text}]")
                freq_run.font.size = Pt(12)
                freq_run.font.name = '宋体'
                freq_run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                if freq_text == '必考':
                    freq_run.font.color.rgb = RGBColor(255, 0, 0)
                elif freq_text == '常考':
                    freq_run.font.color.rgb = RGBColor(255, 153, 0)
                else:
                    freq_run.font.color.rgb = RGBColor(0, 153, 0)
            
            if ep.content:
                format_content(doc, ep.content)
            
            doc.add_paragraph()
    else:
        p = doc.add_paragraph()
        run = p.add_run("暂无考点内容")
        run.font.color.rgb = RGBColor(153, 153, 153)
    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    filename = f"{title_text}.docx"
    encoded_filename = quote(filename)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=\"{encoded_filename}\""}
    )

@router.post("/download-unit/{unit_id}")
def download_unit(
    unit_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    POINTS_COST = 10
    
    if user.points < POINTS_COST:
        raise HTTPException(status_code=400, detail="积分不足")
    
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="单元不存在")
    
    user.points -= POINTS_COST
    
    semester = db.query(Semester).filter(Semester.id == unit.semester_id).first()
    subject = db.query(Subject).filter(Subject.id == semester.subject_id).first() if semester else None
    grade = db.query(Grade).filter(Grade.id == subject.grade_id).first() if subject else None
    
    title = f"{grade.name if grade else ''} {subject.name if subject else ''} {semester.name if semester else ''} - {unit.name} - 知识考点"
    
    order = Order(
        user_id=user.id,
        title=title,
        order_type="knowledge",
        points=POINTS_COST
    )
    db.add(order)
    db.commit()
    
    return {"message": "下载成功", "points": user.points}

@router.post("/set-child-grade")
def set_child_grade(
    data: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    grade_id = data.get('grade_id')
    if not grade_id:
        raise HTTPException(status_code=400, detail="年级ID不能为空")
    
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="年级不存在")
    
    from datetime import datetime
    user.child_grade_id = grade_id
    user.child_grade_set_at = datetime.now()
    db.commit()
    
    return {"message": "设置成功", "grade_name": grade.name}