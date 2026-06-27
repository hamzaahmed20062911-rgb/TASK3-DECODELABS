

from typing import List

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import engine, get_db

# Creates all tables defined in models.py if they don't already exist.
# In a production system this would normally be handled by a migration
# tool (e.g. Alembic) instead of being run automatically on startup.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DecodeLabs Project 3 - Student/Course Database Integration",
    description=(
        "A small backend service demonstrating schema design, CRUD "
        "operations, RESTful routing, and basic data-integrity/security "
        "practices on top of a relational database."
    ),
    version="1.0.0",
)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "service": "Project 3 - Database Integration"}


# ---------------------------------------------------------------------
# Students
# ---------------------------------------------------------------------

@app.post("/students", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED, tags=["students"])
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Student).filter(models.Student.email == student.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return crud.create_student(db, student)


@app.get("/students", response_model=List[schemas.StudentOut], tags=["students"])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_students(db, skip=skip, limit=limit)


@app.get("/students/{student_id}", response_model=schemas.StudentOut, tags=["students"])
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id)
    if db_student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return db_student


@app.put("/students/{student_id}", response_model=schemas.StudentOut, tags=["students"])
def update_student(student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = crud.update_student(db, student_id, updates)
    if db_student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return db_student


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["students"])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_student(db, student_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return None


# ---------------------------------------------------------------------
# Courses
# ---------------------------------------------------------------------

@app.post("/courses", response_model=schemas.CourseOut, status_code=status.HTTP_201_CREATED, tags=["courses"])
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Course).filter(models.Course.code == course.code).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Course code already exists")
    return crud.create_course(db, course)


@app.get("/courses", response_model=List[schemas.CourseOut], tags=["courses"])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_courses(db, skip=skip, limit=limit)


@app.get("/courses/{course_id}", response_model=schemas.CourseOut, tags=["courses"])
def read_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id)
    if db_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return db_course


@app.put("/courses/{course_id}", response_model=schemas.CourseOut, tags=["courses"])
def update_course(course_id: int, updates: schemas.CourseUpdate, db: Session = Depends(get_db)):
    db_course = crud.update_course(db, course_id, updates)
    if db_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return db_course


@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["courses"])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_course(db, course_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return None


# ---------------------------------------------------------------------
# Enrollments (the many-to-many junction)
# ---------------------------------------------------------------------

@app.post("/enrollments", response_model=schemas.EnrollmentOut, status_code=status.HTTP_201_CREATED, tags=["enrollments"])
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    result = crud.create_enrollment(db, enrollment)
    if result == "STUDENT_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    if result == "COURSE_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if result == "ALREADY_ENROLLED":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already enrolled in this course")
    return result


@app.get("/enrollments", response_model=List[schemas.EnrollmentOut], tags=["enrollments"])
def list_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_enrollments(db, skip=skip, limit=limit)


@app.delete("/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["enrollments"])
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_enrollment(db, enrollment_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return None


# ---------------------------------------------------------------------
# Relationship views - showing the many-to-many in action
# ---------------------------------------------------------------------

@app.get("/students/{student_id}/courses", response_model=schemas.StudentWithCourses, tags=["relationships"])
def get_student_courses(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id)
    if db_student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    courses = [e.course for e in db_student.enrollments]
    return schemas.StudentWithCourses(
        id=db_student.id,
        full_name=db_student.full_name,
        email=db_student.email,
        created_at=db_student.created_at,
        courses=courses,
    )


@app.get("/courses/{course_id}/students", response_model=schemas.CourseWithStudents, tags=["relationships"])
def get_course_students(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id)
    if db_course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    students = [e.student for e in db_course.enrollments]
    return schemas.CourseWithStudents(
        id=db_course.id,
        title=db_course.title,
        code=db_course.code,
        credits=db_course.credits,
        created_at=db_course.created_at,
        students=students,
    )
