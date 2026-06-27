# Project 3 — Database Integration
**DecodeLabs Industrial Training Kit | Student/Course Management API**

A small backend service that connects a FastAPI application to a relational
database, built to satisfy the Project 3 brief: design a schema, perform
CRUD operations, and handle data safely.

---

## 1. What this project does

It manages two entities — **Students** and **Courses** — that have a
many-to-many relationship through an **Enrollments** table (a student can
take many courses, a course can have many students). It exposes a full
REST API to create, read, update, and delete records in all three tables.

```
Student (1) ----< Enrollment >---- (1) Course
```

## 2. Tech stack

| Layer            | Choice                                   |
|-------------------|-------------------------------------------|
| Language          | Python 3                                  |
| Web framework     | FastAPI                                   |
| ORM               | SQLAlchemy                                |
| Database          | PostgreSQL (falls back to SQLite if no `DATABASE_URL` is set, so it runs out of the box) |
| Validation        | Pydantic                                  |

## 3. Project structure

```
project3-database-integration/
├── app/
│   ├── main.py        # FastAPI app + all REST routes
│   ├── models.py       # SQLAlchemy schema (tables, keys, constraints)
│   ├── schemas.py       # Pydantic request/response validation
│   ├── crud.py          # Create/Read/Update/Delete database logic
│   └── database.py      # DB connection + session handling
├── sql/
│   └── schema.sql      # Raw SQL version of the schema, for reference
├── requirements.txt
├── .env.example
├── test_run_output.txt # Real terminal output from a full test run
└── README.md
```

## 4. Setup

### Option A — quick start with SQLite (no installation needed)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
That's it — a `school.db` SQLite file is created automatically on first run.

### Option B — PostgreSQL (matches the kit's recommended stack)
1. Create a database:
   ```sql
   CREATE DATABASE school_db;
   ```
2. Set the connection string:
   ```bash
   export DATABASE_URL=postgresql://postgres:your_password@localhost:5432/school_db
   ```
3. Install dependencies and run:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

The app creates all tables automatically on startup — no manual migration
step is required, though `sql/schema.sql` is included if you want to
inspect or run the raw SQL directly.

Once running, open **http://127.0.0.1:8000/docs** for the interactive
Swagger UI — this is the easiest way to test every endpoint by hand and
take your own screenshots for submission.

## 5. Schema design

| Table         | Purpose                                          | Key constraints |
|---------------|---------------------------------------------------|------------------|
| `students`    | One row per student                               | `email` is `UNIQUE` and `NOT NULL` |
| `courses`     | One row per course                                 | `code` is `UNIQUE`; `credits` must be `> 0` (`CHECK` constraint) |
| `enrollments` | Junction table resolving the many-to-many relationship | Composite `UNIQUE(student_id, course_id)` prevents double-enrollment; both columns are `FOREIGN KEY`s |

Full details, including raw `CREATE TABLE` statements, are in
`sql/schema.sql`.

## 6. API reference

| Action | Method | Endpoint                          | SQL operation |
|--------|--------|-------------------------------------|----------------|
| Create student | `POST`   | `/students`                | `INSERT` |
| List students  | `GET`    | `/students`                | `SELECT` |
| Get one student| `GET`    | `/students/{id}`           | `SELECT` |
| Update student | `PUT`    | `/students/{id}`           | `UPDATE` |
| Delete student | `DELETE` | `/students/{id}`           | `DELETE` |
| Create course  | `POST`   | `/courses`                 | `INSERT` |
| List courses   | `GET`    | `/courses`                 | `SELECT` |
| Get one course | `GET`    | `/courses/{id}`            | `SELECT` |
| Update course  | `PUT`    | `/courses/{id}`            | `UPDATE` |
| Delete course  | `DELETE` | `/courses/{id}`            | `DELETE` |
| Enroll student in course | `POST` | `/enrollments`     | `INSERT` |
| List enrollments | `GET`  | `/enrollments`             | `SELECT` |
| Remove enrollment | `DELETE` | `/enrollments/{id}`     | `DELETE` |
| A student's courses | `GET` | `/students/{id}/courses`  | `SELECT` (joined) |
| A course's students | `GET` | `/courses/{id}/students`  | `SELECT` (joined) |

## 7. Data handling & security

- **Validation at the API boundary** — every request body is checked by a
  Pydantic schema before it reaches the database (e.g. emails must be
  valid, course credits must be a positive integer ≤ 10).
- **Validation at the database boundary** — `UNIQUE`, `NOT NULL`, and
  `CHECK` constraints are enforced by the database itself, so the schema
  stays consistent even if application code has a bug.
- **No SQL injection risk** — every query goes through SQLAlchemy's
  query builder, which always uses parameterized queries under the hood.
  No raw string concatenation is used anywhere in `crud.py`.
- **Sensible HTTP status codes** — `201` on create, `204` on delete,
  `404` when a record doesn't exist, `409` on duplicate
  email/course-code/enrollment, `422` on invalid input.

## 8. How this was tested

`test_run_output.txt` contains the real terminal output from running the
server and exercising every endpoint with `curl`: creating students and
courses, listing them, updating a record, enrolling a student, rejecting
a duplicate enrollment, and deleting a course. All requests returned the
expected status codes and data.

For your own submission screenshots, the fastest approach is:
1. Run `uvicorn app.main:app --reload`
2. Open `http://127.0.0.1:8000/docs` in your browser
3. Use the "Try it out" button on a few endpoints
4. Screenshot the Swagger UI showing a request and its response

This gives you authentic, original screenshots of the project running on
your own machine.

## 9. Possible extensions

- Add pagination metadata (total count) to list endpoints
- Add an Alembic migration setup instead of `create_all()`
- Add authentication so students can only update their own record
