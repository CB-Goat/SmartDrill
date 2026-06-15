from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.models import User, Subject, Semester, Unit, KnowledgePoint, Question
from app.utils.auth import get_password_hash
from app.models.models import UserRole

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                password=get_password_hash("admin123"),
                phone="13800138000",
                points=999999,
                role=UserRole.admin
            )
            db.add(admin)
        
        if not db.query(Subject).first():
            subjects_data = [
                {"name": "语文"},
                {"name": "数学"},
                {"name": "英语"},
                {"name": "物理"},
                {"name": "化学"},
                {"name": "生物"}
            ]
            for s in subjects_data:
                subject = Subject(name=s["name"])
                db.add(subject)
            
            db.commit()
            
            for subject in db.query(Subject).all():
                for i in range(1, 3):
                    semester = Semester(subject_id=subject.id, name=f"第{i}学期")
                    db.add(semester)
            
            db.commit()
            
            for semester in db.query(Semester).all():
                for i in range(1, 6):
                    unit = Unit(semester_id=semester.id, name=f"第{i}单元")
                    db.add(unit)
            
            db.commit()
        
        db.commit()
        print("数据库初始化完成")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()