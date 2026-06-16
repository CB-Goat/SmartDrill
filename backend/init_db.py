from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.models import (
    User, AdminUser, Version, Grade, Subject, Semester, Unit, 
    KnowledgePoint, ExamPoint, QuestionType, Difficulty, Question
)
from app.utils.auth import get_password_hash
from app.models.models import ExamFrequency

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        if not db.query(AdminUser).filter(AdminUser.username == "admin").first():
            admin = AdminUser(
                username="admin",
                password=get_password_hash("admin123")
            )
            db.add(admin)
        
        if not db.query(Version).first():
            version = Version(name="人教版")
            db.add(version)
            db.commit()
            
            grades_data = [
                {"name": "三年级", "subjects": ["语文", "数学", "英语"]},
                {"name": "四年级", "subjects": ["语文", "数学", "英语"]},
                {"name": "五年级", "subjects": ["语文", "数学", "英语"]},
                {"name": "六年级", "subjects": ["语文", "数学", "英语"]},
                {"name": "七年级", "subjects": ["语文", "数学", "英语", "历史", "地理", "生物", "道法"]},
                {"name": "八年级", "subjects": ["语文", "数学", "英语", "历史", "地理", "生物", "道法", "物理"]},
                {"name": "九年级", "subjects": ["语文", "数学", "英语", "历史", "道法", "物理", "化学"]}
            ]
            
            for g in grades_data:
                grade = Grade(version_id=version.id, name=g["name"])
                db.add(grade)
                db.commit()
                
                for s in g["subjects"]:
                    subject = Subject(grade_id=grade.id, name=s)
                    db.add(subject)
                    db.commit()
                    
                    for sem in ["上册", "下册"]:
                        semester = Semester(subject_id=subject.id, name=sem)
                        db.add(semester)
                        db.commit()
                        
                        for i in range(1, 6):
                            unit = Unit(semester_id=semester.id, name=f"第{i}单元")
                            db.add(unit)
                    db.commit()
        
        if not db.query(QuestionType).first():
            question_types = ["单选题", "多选题", "连线题", "判断题", "填空题", "解答题", "计算题", "应用题"]
            for qt in question_types:
                db.add(QuestionType(name=qt))
            db.commit()
        
        if not db.query(Difficulty).first():
            difficulties = ["简单", "中等", "困难"]
            for d in difficulties:
                db.add(Difficulty(name=d))
            db.commit()
        
        db.commit()
        print("数据库初始化完成")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()