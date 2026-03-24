"""
Flask application factory
Initializes Flask app with extensions and blueprints
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    
    # Disable template caching in production to see updates immediately
    # (Remove this after confirming the new design works)
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    # Create upload directory if it doesn't exist
    upload_folder = app.config['UPLOAD_FOLDER']
    upload_folder.mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.user import user_bp
    from app.routes.staff import staff_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint (for Render deployment monitoring)
    @app.route('/health')
    def health():
        """Health check endpoint that doesn't require database"""
        return {'status': 'ok', 'service': 'SEAIT Lost and Found System'}, 200
    
    # Root route - redirect to login
    @app.route('/')
    def index():
        from flask import redirect, url_for
        from flask_login import current_user
        try:
            if current_user.is_authenticated:
                # Redirect based on role
                if current_user.is_admin():
                    return redirect(url_for('admin.dashboard'))
                elif current_user.is_staff():
                    return redirect(url_for('staff.dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
        except Exception as e:
            # If there's an error, just redirect to login
            app.logger.error(f"Error in index route: {e}")
        return redirect(url_for('auth.login'))

    @app.errorhandler(413)
    def request_entity_too_large(error):
        from flask import request, redirect, url_for, flash
        from flask_login import current_user
        app.logger.warning(f"413 Payload too large at {request.path}: {error}")
        flash('Uploaded file is too large. Maximum allowed size is 16MB.', 'error')
        # Redirect back if possible, fallback to dashboard/login
        ref = request.referrer
        if ref:
            return redirect(ref)
        return redirect(url_for('user.dashboard') if current_user.is_authenticated else url_for('auth.login'))

    @app.errorhandler(500)
    def internal_error(error):
        from flask import request, redirect, url_for, flash
        from flask_login import current_user
        # Ensure failed transactions do not poison the session for next requests
        try:
            db.session.rollback()
        except Exception:
            pass
        app.logger.exception(f"500 Internal Server Error at {request.path}: {error}")
        flash('Unexpected server issue occurred. Please try again.', 'error')
        if current_user.is_authenticated:
            if current_user.is_admin():
                return redirect(url_for('admin.dashboard'))
            if current_user.is_staff():
                return redirect(url_for('staff.dashboard'))
            return redirect(url_for('user.dashboard'))
        return redirect(url_for('auth.login'))
    
    # Import models to register them with SQLAlchemy
    from app import models
    
    # Create database tables (if they don't exist)
    # This is done in a try-except to prevent startup failures
    with app.app_context():
        try:
            # Test database connection first
            db.engine.connect()
            db.create_all()
            app.logger.info("Database connection successful and tables created/verified")
        except Exception as e:
            # Log the error but don't crash the app
            app.logger.warning(f"Database initialization warning: {e}")
            app.logger.info("App will continue to run, but database operations may fail")
    
    # Context processor for unread notifications
    @app.context_processor
    def inject_unread_count():
        from flask_login import current_user
        from app.services.notification_service import NotificationService
        if current_user.is_authenticated:
            return {'unread_count': NotificationService.get_unread_count(current_user.id)}
        return {'unread_count': 0}
    
    return app
