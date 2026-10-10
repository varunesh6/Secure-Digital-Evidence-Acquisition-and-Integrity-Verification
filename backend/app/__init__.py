import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from config import config

load_dotenv()


# Global DB and app extensions

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200/day", "50/hour"])


@login_manager.user_loader
def load_user(user_id):
    from app.models import User

    return User.query.get(int(user_id))


login_manager.login_view = "auth.login"
login_manager.login_message_category = "error"


def create_app(config_name=None):
    config_name = config_name or os.getenv("FLASK_ENV", "default")
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", ["http://localhost:5173"])}} ,
        supports_credentials=True,
    )

    app.config["JSON_SORT_KEYS"] = False

    from app.models import Role, User

    with app.app_context():
        db.create_all()
        for role_name in ["Administrator", "Investigator", "Auditor"]:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name, description=f"{role_name} access"))
        db.session.commit()

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error", "message": str(error)}), 500

    from app.routes.auth import auth_bp
    from app.routes.cases import cases_bp
    from app.routes.evidence import evidence_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.reports import reports_bp
    from app.routes.admin import admin_bp
    from app.routes.notifications import notifications_bp
    from app.routes.audit import audit_bp
    from app.routes.custody import custody_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(cases_bp, url_prefix="/api")
    app.register_blueprint(evidence_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(notifications_bp, url_prefix="/api")
    app.register_blueprint(audit_bp, url_prefix="/api")
    app.register_blueprint(custody_bp, url_prefix="/api")

    os.makedirs(app.config["EVIDENCE_STORAGE_PATH"], exist_ok=True)

    return app
