

from sqlalchemy import (
    Column, Integer, String, ForeignKey, CheckConstraint, UniqueConstraint,
    DateTime, func
)
from sqlalchemy.orm import relationship

from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    enrollments = relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan"
    )


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    credits = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("credits > 0", name="ck_courses_credits_positive"),
    )

    enrollments = relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )


class Enrollment(Base):
    """Junction table resolving the Student <-> Course many-to-many
    relationship. Each row represents one student's enrollment in one
    course."""

    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
