"""
Helper utility functions
"""
from functools import wraps
from flask import abort, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
from datetime import datetime

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file, subfolder: str = 'items') -> str:
    """
    Save uploaded file and return relative path
    Returns path relative to static folder
    """
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Create subfolder path
        upload_folder = current_app.config['UPLOAD_FOLDER']
        subfolder_path = upload_folder / subfolder
        subfolder_path.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = subfolder_path / unique_filename
        file.save(str(file_path))
        
        # Return relative path from static folder
        return f"uploads/{subfolder}/{unique_filename}"
    
    return None

def role_required(*roles):
    """
    Decorator to require specific roles for a route
    Usage: @role_required('admin', 'staff')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
