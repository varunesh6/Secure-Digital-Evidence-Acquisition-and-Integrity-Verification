from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.models import AuditLog, CustodyTransfer, Evidence, Notification, User

custody_bp = Blueprint("custody", __name__)


@custody_bp.route("/custody/transfer", methods=["POST"])
@login_required
def initiate_transfer():
    if current_user.role.name not in {"Administrator", "Investigator"}:
        return jsonify({"error": "Unauthorized."}), 403

    data = request.get_json(silent=True) or {}
    evidence_id = data.get("evidence_id")
    to_user_id = data.get("to_user_id")
    reason = data.get("reason", "")

    if not evidence_id or not to_user_id:
        return jsonify({"error": "Evidence ID and recipient ID are required."}), 400

    evidence = Evidence.query.get_or_404(evidence_id)
    recipient = User.query.get_or_404(to_user_id)
    transfer = CustodyTransfer(
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        from_user_id=current_user.id,
        to_user_id=recipient.id,
        reason=reason,
        status="PENDING",
    )
    db.session.add(transfer)
    db.session.flush()

    db.session.add(Notification(
        user_id=recipient.id,
        notification_type="PENDING_CUSTODY_TRANSFER",
        message=f"Custody transfer initiated for evidence #{evidence.id}.",
        linked_record=f"evidence:{evidence.id}",
    ))
    db.session.add(AuditLog(
        user_id=current_user.id,
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        action_type="CUSTODY_TRANSFER_INITIATED",
        description=f"Transfer initiated from {current_user.username} to {recipient.username}",
        details=str({"to_user": recipient.id, "reason": reason}),
    ))
    db.session.commit()
    return jsonify({"message": "Transfer initiated.", "transfer_id": transfer.id})


@custody_bp.route("/custody/<int:transfer_id>/accept", methods=["POST"])
@login_required
def accept_transfer(transfer_id):
    transfer = CustodyTransfer.query.get_or_404(transfer_id)
    evidence = Evidence.query.get_or_404(transfer.evidence_id)
    if current_user.id != transfer.to_user_id:
        return jsonify({"error": "Only the designated recipient can accept custody."}), 403

    evidence.current_custodian_id = current_user.id
    evidence.status = "IN_CUSTODY"
    transfer.status = "ACCEPTED"
    transfer.accepted_at = datetime.now(timezone.utc)

    db.session.add(AuditLog(
        user_id=current_user.id,
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        action_type="CUSTODY_TRANSFER_ACCEPTED",
        description=f"Custody accepted by {current_user.username}",
        details=str({"from_user": transfer.from_user_id, "to_user": transfer.to_user_id}),
    ))
    db.session.commit()
    return jsonify({"message": "Custody transfer accepted.", "evidence_id": evidence.id})


@custody_bp.route("/custody/<int:evidence_id>", methods=["GET"])
@login_required
def list_transfers(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    records = CustodyTransfer.query.filter_by(evidence_id=evidence_id).order_by(CustodyTransfer.initiated_at.desc()).all()
    return jsonify({"transfers": [{
        "id": r.id,
        "status": r.status,
        "from_user_id": r.from_user_id,
        "to_user_id": r.to_user_id,
        "reason": r.reason,
        "initiated_at": r.initiated_at.isoformat(),
        "accepted_at": r.accepted_at.isoformat() if r.accepted_at else None,
    } for r in records]})
