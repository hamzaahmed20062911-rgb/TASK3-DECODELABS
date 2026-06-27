

CREATE TABLE IF NOT EXISTS students (
    id          SERIAL PRIMARY KEY,
    full_name   VARCHAR(120) NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS courses (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(150) NOT NULL,
    code        VARCHAR(20)  NOT NULL UNIQUE,
    credits     INTEGER NOT NULL CHECK (credits > 0),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Junction table resolving the Student <-> Course many-to-many relationship
CREATE TABLE IF NOT EXISTS enrollments (
    id           SERIAL PRIMARY KEY,
    student_id   INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id    INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    enrolled_at  TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_student_course UNIQUE (student_id, course_id)
);

CREATE INDEX IF NOT EXISTS idx_enrollments_student_id ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);
