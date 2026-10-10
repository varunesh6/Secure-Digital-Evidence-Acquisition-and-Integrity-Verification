from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from app.models import AuditLog


audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/audit-logs", methods=["GET"])
@login_required
def list_audit_logs():
    if current_user.role.name not in {"Administrator", "Investigator", "Auditor"}:
        return jsonify({"error": "Unauthorized."}), 403

    rows = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    payload = [{
        "id": row.id,
        "action_type": row.action_type,
        "description": row.description,
        "timestamp": row.timestamp.isoformat(),
        "user_id": row.user_id,
        "evidence_id": row.evidence_id,
        "case_id": row.case_id,
    } for row in rows]
    return jsonify({"logs": payload})
