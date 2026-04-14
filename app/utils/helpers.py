from functools import wraps
from pathlib import Path
import uuid

from flask import abort, current_app, flash, redirect, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def save_uploaded_file(file, subfolder: str) -> str | None:
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        subfolder_path = Path(upload_folder) / subfolder
        subfolder_path.mkdir(parents=True, exist_ok=True)

        file_path = subfolder_path / unique_filename
        file.save(str(file_path))

        return f"uploads/{subfolder}/{unique_filename}"

    return None


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                flash("You are not authorized to access this page.", "danger")
                return abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
