from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class ExamFrequency(str, enum.Enum):
    seldom = "少考"
    often = "常考"
    must = "必考"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20))
    points = Column(Integer, default=0)
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recharges = relationship("Recharge", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Recharge(Base):
    __tablename__ = "recharges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    points = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="recharges")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    order_type = Column(String(50), nullable=False)
    points = Column(Integer, nullable=False)
    file_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="orders")

class Version(Base):
    __tablename__ = "versions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    grades = relationship("Grade", back_populates="version")

class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id"), nullable=False)
    name = Column(String(50), nullable=False)
    subjects = relationship("Subject", back_populates="grade")
    version = relationship("Version", back_populates="grades")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=False)
    name = Column(String(100), nullable=False)
    semesters = relationship("Semester", back_populates="subject")
    grade = relationship("Grade", back_populates="subjects")

class Semester(Base):
    __tablename__ = "semesters"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    units = relationship("Unit", back_populates="semester")
    subject = relationship("Subject", back_populates="semesters")

class Unit(Base):
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semesters.id"), nullable=False)
    name = Column(String(100), nullable=False)
    knowledge_points = relationship("KnowledgePoint", back_populates="unit")
    semester = relationship("Semester", back_populates="units")

class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    
    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    exam_points = relationship("ExamPoint", back_populates="knowledge_point")
    unit = relationship("Unit", back_populates="knowledge_points")
    created_at = Column(DateTime, default=datetime.utcnow)

class ExamPoint(Base):
    __tablename__ = "exam_points"
    
    id = Column(Integer, primary_key=True, index=True)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    exam_types = Column(String(255))
    exam_frequency = Column(Enum(ExamFrequency), default=ExamFrequency.often)
    questions = relationship("Question", back_populates="exam_point")
    knowledge_point = relationship("KnowledgePoint", back_populates="exam_points")
    created_at = Column(DateTime, default=datetime.utcnow)

class QuestionType(Base):
    __tablename__ = "question_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    questions = relationship("Question", back_populates="question_type_obj")

class Difficulty(Base):
    __tablename__ = "difficulties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    questions = relationship("Question", back_populates="difficulty_obj")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("versions.id"))
    grade_id = Column(Integer, ForeignKey("grades.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))
    unit_id = Column(Integer, ForeignKey("units.id"))
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"))
    exam_point_id = Column(Integer, ForeignKey("exam_points.id"))
    question_type_id = Column(Integer, ForeignKey("question_types.id"))
    difficulty_id = Column(Integer, ForeignKey("difficulties.id"))
    
    content = Column(Text, nullable=False)
    options = Column(Text)
    answer = Column(Text, nullable=False)
    analysis = Column(Text)
    
    question_type_obj = relationship("QuestionType", back_populates="questions")
    difficulty_obj = relationship("Difficulty", back_populates="questions")
    exam_point = relationship("ExamPoint", back_populates="questions")
    
    created_at = Column(DateTime, default=datetime.utcnow)