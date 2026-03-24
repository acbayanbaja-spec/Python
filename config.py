"""
Configuration settings for the Lost and Found System
Supports PostgreSQL (production) and SQLite (development)
"""
import os
from pathlib import Path

basedir = Path(__file__).parent.absolute()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # ✅ FORCE PostgreSQL (Render production)
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # 🔥 Fallback to your ACTUAL Render database if env variable is missing
    if not DATABASE_URL:
        DATABASE_URL = "postgresql://python_uav0_user:hoXETU46jC6RQz9L0ttnMyDOarW5pjxV@dpg-d711ekvfte5s739rume0-a.singapore-postgres.render.com:5432/python_uav0"

    # ✅ Fix old postgres:// format
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Upload configuration
    UPLOAD_FOLDER = basedir / 'app' / 'static' / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Session configuration
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Pagination
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig  # ✅ force production
}
