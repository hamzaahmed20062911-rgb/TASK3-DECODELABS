

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from . import models, schemas


# ---------- Student CRUD ----------

def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(full_name=student.full_name, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_student(db: Session, student_id: int) -> models.Student | None:
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_students(db: Session, skip: int = 0, limit: int = 100) -> list[models.Student]:
    return db.query(models.Student).offset(skip).limit(limit).all()


def update_student(db: Session, student_id: int, updates: schemas.StudentUpdate) -> models.Student | None:
    db_student = get_student(db, student_id)
    if db_student is None:
        return None
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    db_student = get_student(db, student_id)
    if db_student is None:
        return False
    db.delete(db_student)
    db.commit()
    return True


# ---------- Course CRUD ----------

def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    db_course = models.Course(title=course.title, code=course.code, credits=course.credits)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_course(db: Session, course_id: int) -> models.Course | None:
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def get_courses(db: Session, skip: int = 0, limit: int = 100) -> list[models.Course]:
    return db.query(models.Course).offset(skip).limit(limit).all()


def update_course(db: Session, course_id: int, updates: schemas.CourseUpdate) -> models.Course | None:
    db_course = get_course(db, course_id)
    if db_course is None:
        return None
    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, course_id: int) -> bool:
    db_course = get_course(db, course_id)
    if db_course is None:
        return False
    db.delete(db_course)
    db.commit()
    return True


# ---------- Enrollment (many-to-many junction) ----------

def create_enrollment(db: Session, enrollment: schemas.EnrollmentCreate) -> models.Enrollment | str:
    """Returns the created Enrollment, or a short error string if the
    student/course doesn't exist or the enrollment already exists."""
    student = get_student(db, enrollment.student_id)
    if student is None:
        return "STUDENT_NOT_FOUND"

    course = get_course(db, enrollment.course_id)
    if course is None:
        return "COURSE_NOT_FOUND"

    db_enrollment = models.Enrollment(
        student_id=enrollment.student_id, course_id=enrollment.course_id
    )
    db.add(db_enrollment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return "ALREADY_ENROLLED"
    db.refresh(db_enrollment)
    return db_enrollment


def get_enrollments(db: Session, skip: int = 0, limit: int = 100) -> list[models.Enrollment]:
    return db.query(models.Enrollment).offset(skip).limit(limit).all()


def delete_enrollment(db: Session, enrollment_id: int) -> bool:
    db_enrollment = db.query(models.Enrollment).filter(models.Enrollment.id == enrollment_id).first()
    if db_enrollment is None:
        return False
    db.delete(db_enrollment)
    db.commit()
    return True
