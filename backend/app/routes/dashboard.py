from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app.models import AuditLog, Case, CustodyTransfer, Evidence, EvidenceVerification, User


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    if current_user.role.name not in {"Administrator", "Investigator", "Auditor"}:
        return jsonify({"error": "Unauthorized."}), 403

    total_cases = Case.query.count()
    open_cases = Case.query.filter(Case.status == "OPEN").count()
    total_evidence = Evidence.query.count()
    verified_successfully = EvidenceVerification.query.filter_by(result="INTEGRITY VERIFIED").count()
    mismatches = EvidenceVerification.query.filter_by(result="INTEGRITY MISMATCH").count()

    recent_activity = [
        {"action_type": a.action_type, "description": a.description, "timestamp": a.timestamp.isoformat()} for a in AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    ]
    recent_verifications = [
        {"evidence_id": v.evidence_id, "result": v.result, "verification_timestamp": v.verification_timestamp.isoformat()} for v in EvidenceVerification.query.order_by(EvidenceVerification.verification_timestamp.desc()).limit(10).all()
    ]

    status_distribution = []
    for status in ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]:
        status_distribution.append({"name": status, "value": Case.query.filter(Case.status == status).count()})

    file_type_distribution = []
    file_types = Evidence.query.with_entities(Evidence.file_type).all()
    counts = {}
    for item in file_types:
        counts[item[0]] = counts.get(item[0], 0) + 1
    for name, value in counts.items():
        file_type_distribution.append({"name": name, "value": value})

    return jsonify({
        "stats": {
            "total_cases": total_cases,
            "open_cases": open_cases,
            "total_registered_evidence": total_evidence,
            "evidence_verified_successfully": verified_successfully,
            "evidence_with_integrity_mismatches": mismatches,
            "pending_custody_transfers": CustodyTransfer.query.filter_by(status="PENDING").count(),
        },
        "recent_activity": recent_activity,
        "recent_verifications": recent_verifications,
        "case_status_distribution": status_distribution,
        "evidence_file_type_distribution": file_type_distribution,
    })
