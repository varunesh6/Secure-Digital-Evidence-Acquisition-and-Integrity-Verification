from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.models import Case, Role, User

cases_bp = Blueprint("cases", __name__)


def allowed_case_access(user, case_item):
    if user.role.name == "Administrator":
        return True
    if user.role.name == "Auditor":
        return True
    if user.role.name == "Investigator":
        return user.id == case_item.created_by_id or user.id == case_item.assigned_investigator_id
    return False


@cases_bp.route("/cases", methods=["GET"]) 
@login_required
def list_cases():
    if current_user.role.name not in {"Administrator", "Investigator", "Auditor"}:
        return jsonify({"error": "Unauthorized."}), 403

    q = request.args.get("q", "").strip()
    status = request.args.get("status")
    priority = request.args.get("priority")
    investigator = request.args.get("investigator")

    query = Case.query
    if q:
        query = query.filter((Case.case_number.like(f"%{q}%")) | (Case.title.like(f"%{q}%")))
    if status:
        query = query.filter(Case.status == status)
    if priority:
        query = query.filter(Case.priority == priority)
    if investigator:
        query = query.filter(Case.assigned_investigator_id == int(investigator))

    if current_user.role.name == "Investigator":
        query = query.filter((Case.created_by_id == current_user.id) | (Case.assigned_investigator_id == current_user.id))

    items = query.order_by(Case.created_at.desc()).all()
    payload = [{
        "id": c.id,
        "case_number": c.case_number,
        "title": c.title,
        "description": c.description,
        "incident_category": c.incident_category,
        "priority": c.priority,
        "status": c.status,
        "assigned_investigator_id": c.assigned_investigator_id,
        "created_by_id": c.created_by_id,
        "notes": c.notes,
        "created_at": c.created_at.isoformat(),
    } for c in items]
    return jsonify({"cases": payload})


@cases_bp.route("/cases", methods=["POST"])
@login_required
def create_case():
    if current_user.role.name not in {"Administrator", "Investigator"}:
        return jsonify({"error": "Unauthorized."}), 403

    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    incident_category = (data.get("incident_category") or "").strip()
    priority = (data.get("priority") or "MEDIUM").strip().upper()
    status = (data.get("status") or "OPEN").strip().upper()
    assigned_investigator_id = data.get("assigned_investigator_id")

    if not title or not incident_category:
        return jsonify({"error": "Title and incident category are required."}), 400

    case_number = f"CASE-{len(Case.query.all()) + 1:04d}"
    case = Case(
        case_number=case_number,
        title=title,
        description=description,
        incident_category=incident_category,
        priority=priority,
        status=status,
        assigned_investigator_id=int(assigned_investigator_id) if assigned_investigator_id else current_user.id,
        created_by_id=current_user.id,
        notes=data.get("notes", ""),
    )
    db.session.add(case)
    db.session.commit()
    return jsonify({"message": "Case created.", "case": {
        "id": case.id,
        "case_number": case.case_number,
        "title": case.title,
        "description": case.description,
        "incident_category": case.incident_category,
        "priority": case.priority,
        "status": case.status,
        "assigned_investigator_id": case.assigned_investigator_id,
        "created_by_id": case.created_by_id,
    }}), 201


@cases_bp.route("/cases/<int:case_id>", methods=["GET"]) 
@login_required
def get_case(case_id):
    case = Case.query.get_or_404(case_id)
    if not allowed_case_access(current_user, case):
        return jsonify({"error": "Unauthorized to view this case."}), 403
    return jsonify({"case": {
        "id": case.id,
        "case_number": case.case_number,
        "title": case.title,
        "description": case.description,
        "incident_category": case.incident_category,
        "priority": case.priority,
        "status": case.status,
        "assigned_investigator_id": case.assigned_investigator_id,
        "created_by_id": case.created_by_id,
        "notes": case.notes,
        "created_at": case.created_at.isoformat(),
    }})


@cases_bp.route("/cases/<int:case_id>", methods=["PATCH"])
@login_required
def update_case(case_id):
    case = Case.query.get_or_404(case_id)
    if current_user.role.name not in {"Administrator", "Investigator"}:
        return jsonify({"error": "Unauthorized."}), 403
    data = request.get_json(silent=True) or {}
    for field in ["title", "description", "incident_category", "priority", "status", "notes"]:
        if field in data:
            setattr(case, field, data[field])
    db.session.commit()
    return jsonify({"message": "Case updated.", "case": {"id": case.id, "status": case.status}})
