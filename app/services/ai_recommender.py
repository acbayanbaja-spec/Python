from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.subject import StudentSubjectCompletion, Subject
from app.models.user import User


def _build_student_profile(student, completed_codes):
    return f"year{student.year_level} {' '.join(completed_codes)}"


def recommend_subjects(student_id):
    student = User.query.get(student_id)
    if not student:
        return []

    completed = StudentSubjectCompletion.query.filter_by(student_id=student_id).all()
    completed_codes = [row.subject.code for row in completed if row.subject]
    candidates = Subject.query.filter_by(program="BSIT", year_level=student.year_level).all()
    if not candidates:
        return []

    student_doc = _build_student_profile(student, completed_codes)
    subject_docs = [
        f"{sub.code} {sub.title} {sub.description or ''} prereq {sub.prerequisites or ''}"
        for sub in candidates
    ]

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform([student_doc] + subject_docs)
    scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()

    ranked = sorted(zip(candidates, scores), key=lambda item: item[1], reverse=True)
    recommendations = []
    completed_set = set(completed_codes)
    for subject, score in ranked:
        if subject.code in completed_set:
            continue
        prereqs = [p.strip() for p in (subject.prerequisites or "").split(",") if p.strip()]
        missing = [p for p in prereqs if p not in completed_set]
        recommendations.append(
            {
                "code": subject.code,
                "title": subject.title,
                "score": round(float(score), 3),
                "missing_prerequisites": missing,
            }
        )

    return recommendations[:6]


def detect_irregular_status(student_id):
    student = User.query.get(student_id)
    if not student:
        return {"is_irregular": False, "reason": "Student not found."}

    required_subjects = Subject.query.filter_by(program="BSIT", year_level=student.year_level).count()
    completed_count = StudentSubjectCompletion.query.filter_by(student_id=student_id).count()

    is_irregular = completed_count < max(1, required_subjects // 2)
    reason = (
        "Student may be irregular due to low completion count for current year level."
        if is_irregular
        else "Student progression appears regular."
    )
    return {"is_irregular": is_irregular, "reason": reason}
