from app import db


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    units = db.Column(db.Integer, default=3)
    year_level = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    program = db.Column(db.String(120), nullable=False)
    prerequisites = db.Column(db.Text, nullable=True)


class StudentSubjectCompletion(db.Model):
    __tablename__ = "student_subject_completions"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False, index=True)
    grade = db.Column(db.String(10), nullable=True)

    student = db.relationship("User")
    subject = db.relationship("Subject")
