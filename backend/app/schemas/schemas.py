from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    phone: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    phone: Optional[str]
    points: int

    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class RechargeRequest(BaseModel):
    amount: int

class ReviewRequest(BaseModel):
    subjectId: int
    semesterId: int
    unitId: int

class PracticeRequest(BaseModel):
    subjectId: int
    semesterId: int
    unitId: int
    examType: str
    difficulty: str
    questionCount: int

class OrderResponse(BaseModel):
    id: int
    title: str
    points: int
    created_at: datetime
    
    class Config:
        from_attributes = True