import time
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def _init_db_with_retry(app, retries=3, delay=2):
    for attempt in range(1, retries + 1):
        try:
            db.session.execute(text("SELECT 1"))
            db.create_all()
            app.logger.info("Database initialized successfully")
            return
        except SQLAlchemyError as exc:
            app.logger.warning("Database initialization attempt %s failed: %s", attempt, exc)
            db.session.rollback()
            if attempt < retries:
                time.sleep(delay)
    app.logger.warning("App started without active database connection")


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config["default"]))

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)

    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.registrar import registrar_bp
    from app.routes.accounting import accounting_bp
    from app.routes.admin import admin_bp
    from app.routes.sao import sao_bp
    from app.routes.department import department_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(student_bp, url_prefix="/student")
    app.register_blueprint(registrar_bp, url_prefix="/registrar")
    app.register_blueprint(accounting_bp, url_prefix="/accounting")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(sao_bp, url_prefix="/sao")
    app.register_blueprint(department_bp, url_prefix="/department")

    @app.route("/")
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        role_to_endpoint = {
            "student": "student.dashboard",
            "registrar": "registrar.dashboard",
            "accounting": "accounting.dashboard",
            "admin": "admin.dashboard",
            "sao": "sao.dashboard",
            "department": "department.dashboard",
        }
        return redirect(url_for(role_to_endpoint.get(current_user.role, "auth.login")))

    @app.route("/health")
    def health():
        return {"status": "ok", "service": "SEAIT Online Enrollment System"}, 200

    @app.context_processor
    def inject_notification_count():
        if not current_user.is_authenticated:
            return {"unread_count": 0}
        from app.services.notification_service import NotificationService

        return {"unread_count": NotificationService.get_unread_count(current_user.id)}

    with app.app_context():
        from app import models  # noqa: F401

        _init_db_with_retry(app)

    return app
