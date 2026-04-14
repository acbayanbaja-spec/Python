from app import create_app, db
from app.models.enrollment import Enrollment
from app.models.subject import StudentSubjectCompletion, Subject
from app.models.user import User


def _create_user(full_name, email, role, password, student_number=None, year_level=1):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(
        full_name=full_name,
        email=email,
        role=role,
        student_number=student_number,
        year_level=year_level,
    )
    user.set_password(password)
    db.session.add(user)
    return user


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        admin = _create_user("SEAIT Admin", "admin@seait.edu", "admin", "admin123")
        _create_user("SEAIT Registrar", "registrar@seait.edu", "registrar", "registrar123")
        _create_user("SEAIT Accounting", "accounting@seait.edu", "accounting", "accounting123")
        _create_user("SEAIT SAO Officer", "sao@seait.edu", "sao", "sao123")
        _create_user("SEAIT Department Chair", "department@seait.edu", "department", "department123")
        student = _create_user("Juan Dela Cruz", "student@seait.edu", "student", "student123", "2026-0001", 1)

        db.session.commit()

        subjects = [
            ("IT101", "Introduction to Computing", 1, "1st Semester", "", "Basic concepts in computing."),
            ("IT102", "Programming 1", 1, "1st Semester", "", "Python programming fundamentals."),
            ("IT201", "Data Structures", 2, "1st Semester", "IT102", "Core data structures."),
            ("IT202", "Database Systems", 2, "2nd Semester", "IT102", "Relational databases."),
            ("IT301", "Software Engineering", 3, "1st Semester", "IT201, IT202", "SE process and design."),
        ]
        for code, title, year_level, semester, prereq, desc in subjects:
            if not Subject.query.filter_by(code=code).first():
                db.session.add(
                    Subject(
                        code=code,
                        title=title,
                        program="BSIT",
                        year_level=year_level,
                        semester=semester,
                        prerequisites=prereq,
                        description=desc,
                        units=3,
                    )
                )
        db.session.commit()

        first_subject = Subject.query.filter_by(code="IT101").first()
        if first_subject and not StudentSubjectCompletion.query.filter_by(student_id=student.id, subject_id=first_subject.id).first():
            db.session.add(StudentSubjectCompletion(student_id=student.id, subject_id=first_subject.id, grade="1.5"))

        if not Enrollment.query.filter_by(student_id=student.id).first():
            db.session.add(
                Enrollment(
                    student_id=student.id,
                    semester="1st Semester",
                    school_year="2026-2027",
                    program="BSIT",
                    year_level=1,
                    status="pending_registrar",
                    is_draft=False,
                    is_new_student=True,
                    notes="Seeded enrollment sample.",
                )
            )

        db.session.commit()
        print("Seed complete. Admin login: admin@seait.edu / admin123")


if __name__ == "__main__":
    seed()
