from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash

from app import db
from app.models import Role, User

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin/users", methods=["GET"])
@login_required
def list_users():
    if current_user.role.name != "Administrator":
        return jsonify({"error": "Unauthorized."}), 403
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role.name if u.role else "Unknown",
        "is_active": u.is_active,
    } for u in users]})


@admin_bp.route("/admin/users", methods=["POST"])
@login_required
def create_user():
    if current_user.role.name != "Administrator":
        return jsonify({"error": "Unauthorized."}), 403

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    email = (data.get("email") or "").strip()
    full_name = (data.get("full_name") or "").strip()
    role_name = (data.get("role") or "Investigator").strip()

    if not all([username, password, email, full_name]):
        return jsonify({"error": "All user fields are required."}), 400
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        role = Role(name=role_name, description=f"{role_name} role")
        db.session.add(role)
        db.session.flush()

    user = User(username=username, email=email, full_name=full_name, password_hash=generate_password_hash(password), role_id=role.id, is_active=True)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created.", "user": {"id": user.id, "username": user.username, "role": role.name}}), 201
