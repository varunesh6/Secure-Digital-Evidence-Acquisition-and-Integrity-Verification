from flask import Blueprint, jsonify, request, session
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, limiter
from app.models import Role, User


auth_bp = Blueprint("auth", __name__)


def user_response(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.name if user.role else "Unknown",
        "role_id": user.role_id,
        "is_active": user.is_active,
    }


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5/minute")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    user = User.query.filter((User.username == username) | (User.email == username)).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password."}), 401

    if not user.is_active:
        return jsonify({"error": "This account is disabled."}), 403

    login_user(user)
    session.permanent = True
    return jsonify({"message": "Login successful.", "user": user_response(user)})


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    return jsonify({"message": "Logged out successfully."})


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({"user": user_response(current_user)})


@auth_bp.route("/setup-admin", methods=["POST"])
def setup_admin():
    if User.query.count() > 0:
        return jsonify({"error": "Admin setup is disabled once users already exist."}), 403

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    full_name = (data.get("full_name") or "").strip()
    password = data.get("password") or ""

    if not all([username, email, full_name, password]):
        return jsonify({"error": "Username, email, full name and password are required."}), 400

    role = Role.query.filter_by(name="Administrator").first()
    if not role:
        role = Role(name="Administrator", description="System administrator")
        db.session.add(role)
        db.session.flush()

    user = User(
        username=username,
        email=email,
        full_name=full_name,
        password_hash=generate_password_hash(password),
        role_id=role.id,
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Administrator account created.", "user": user_response(user)})
