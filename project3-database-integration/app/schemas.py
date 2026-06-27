

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ---------- Student ----------

class StudentBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120, examples=["Alice Johnson"])
    email: EmailStr = Field(..., examples=["alice@example.com"])


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=120)
    email: Optional[EmailStr] = None


class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Course ----------

class CourseBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=150, examples=["Database Systems"])
    code: str = Field(..., min_length=2, max_length=20, examples=["CS301"])
    credits: int = Field(..., gt=0, le=10, examples=[3])


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = Field(None, min_length=2, max_length=20)
    credits: Optional[int] = Field(None, gt=0, le=10)


class CourseOut(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Enrollment ----------

class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime


class StudentWithCourses(StudentOut):
    courses: List[CourseOut] = []


class CourseWithStudents(CourseOut):
    students: List[StudentOut] = []
