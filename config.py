"""
Configuration settings for the Lost and Found System
Supports PostgreSQL (production) and SQLite (development)
"""
import os
from pathlib import Path
import re

basedir = Path(__file__).parent.absolute()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    # NOTE: Render env vars can sometimes accidentally include extra text/newlines.
    # We defensively extract the first valid postgres URL so SQLAlchemy can parse it.
    _raw_database_url = os.environ.get('DATABASE_URL') or os.environ.get('\ufeffDATABASE_URL')
    DATABASE_URL = None
    if _raw_database_url:
        raw = str(_raw_database_url).strip()
        # Remove wrapping quotes if present (single and double)
        raw = raw.strip("\"' ")
        # If the string contains labels or multiple tokens, extract the first URL.
        m = re.search(r'(postgres(?:ql)?:\/\/[^\s]+)', raw, flags=re.IGNORECASE)
        if m:
            DATABASE_URL = m.group(1)
        else:
            DATABASE_URL = raw
    
    if DATABASE_URL:
        # PostgreSQL (production)
        # Convert postgres:// to postgresql:// if needed (for newer psycopg2)
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # SQLite (development)
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{basedir / "lost_found.db"}'
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

    # Assistant UI (optional overrides via environment)
    # Place your photo or logo in app/static/images/ (e.g. my-chatbot.png) and set:
    # CHATBOT_AVATAR_STATIC=images/my-chatbot.png
    CHATBOT_AVATAR_STATIC = os.environ.get(
        'CHATBOT_AVATAR_STATIC', 'images/chatbot-mascot.svg'
    ).strip()
    CHATBOT_ASSISTANT_NAME = os.environ.get(
        'CHATBOT_ASSISTANT_NAME', 'SEAIT Assistant'
    ).strip() or 'SEAIT Assistant'


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
