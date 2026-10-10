import hashlib
import os
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request, send_file
from flask_login import current_user, login_required

from app import db
from app.models import AuditLog, Case, Evidence, EvidenceVerification, Notification, User
from app.services.evidence_service import allowed_file, compute_sha256, save_uploaded_file, sha256_for_bytes


evidence_bp = Blueprint("evidence", __name__)


def can_view_evidence(user, evidence_item):
    if user.role.name == "Administrator":
        return True
    if user.role.name == "Auditor":
        return True
    if user.role.name == "Investigator":
        return evidence_item.case_id in [c.id for c in user_cases(user)]
    return False


def user_cases(user):
    from app.models import Case

    return Case.query.filter((Case.created_by_id == user.id) | (Case.assigned_investigator_id == user.id)).all()


@evidence_bp.route("/evidence", methods=["GET"])
@login_required
def list_evidence():
    if current_user.role.name not in {"Administrator", "Investigator", "Auditor"}:
        return jsonify({"error": "Unauthorized."}), 403

    q = request.args.get("q", "").strip()
    file_type = request.args.get("file_type")
    status = request.args.get("status")
    case_id = request.args.get("case_id")

    query = Evidence.query
    if q:
        query = query.filter((Evidence.original_filename.like(f"%{q}%")) | (Evidence.stored_filename.like(f"%{q}%")))
    if file_type:
        query = query.filter(Evidence.file_type == file_type)
    if status:
        query = query.filter(Evidence.status == status)
    if case_id:
        query = query.filter(Evidence.case_id == int(case_id))

    if current_user.role.name == "Investigator":
        case_ids = [c.id for c in user_cases(current_user)]
        query = query.filter(Evidence.case_id.in_(case_ids))

    items = query.order_by(Evidence.created_at.desc()).all()
    payload = [{
        "id": e.id,
        "case_id": e.case_id,
        "original_filename": e.original_filename,
        "stored_filename": e.stored_filename,
        "file_size": e.file_size,
        "file_type": e.file_type,
        "source_device": e.source_device,
        "acquisition_method": e.acquisition_method,
        "acquisition_timestamp": e.acquisition_timestamp.isoformat() if e.acquisition_timestamp else None,
        "acquiring_investigator_id": e.acquiring_investigator_id,
        "original_sha256": e.original_sha256,
        "current_custodian_id": e.current_custodian_id,
        "status": e.status,
        "storage_path": e.storage_path,
    } for e in items]
    return jsonify({"evidence": payload})


@evidence_bp.route("/evidence/upload", methods=["POST"])
@login_required
def upload_evidence():
    if current_user.role.name not in {"Administrator", "Investigator"}:
        return jsonify({"error": "Unauthorized."}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file_obj = request.files["file"]
    if file_obj.filename == "":
        return jsonify({"error": "No file selected."}), 400
    if not allowed_file(file_obj.filename):
        return jsonify({"error": "File type not allowed."}), 400

    case_id = request.form.get("case_id")
    if not case_id:
        return jsonify({"error": "Case ID is required."}), 400

    case = Case.query.get(int(case_id))
    if not case:
        return jsonify({"error": "Case not found."}), 404

    storage_root = current_app.config["EVIDENCE_STORAGE_PATH"]
    saved_path, saved_name = save_uploaded_file(file_obj, storage_root)

    try:
        sha256 = compute_sha256(saved_path)
        evidence = Evidence(
            case_id=case.id,
            original_filename=file_obj.filename,
            stored_filename=saved_name,
            storage_path=saved_path,
            file_size=os.path.getsize(saved_path),
            file_type=file_obj.filename.rsplit(".", 1)[1].lower() if "." in file_obj.filename else "unknown",
            source_device=request.form.get("source_device", "N/A"),
            acquisition_method=request.form.get("acquisition_method", "FILE_UPLOAD"),
            acquisition_timestamp=datetime.now(timezone.utc),
            acquiring_investigator_id=current_user.id,
            original_sha256=sha256,
            current_custodian_id=current_user.id,
            status="REGISTERED",
        )
        db.session.add(evidence)
        db.session.flush()

        audit = AuditLog(
            user_id=current_user.id,
            evidence_id=evidence.id,
            case_id=case.id,
            action_type="EVIDENCE_REGISTERED",
            description=f"Evidence registered: {file_obj.filename}",
            details=str({"filename": file_obj.filename, "sha256": sha256}),
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({"message": "Evidence uploaded and recorded.", "evidence": {
            "id": evidence.id,
            "case_id": evidence.case_id,
            "original_filename": evidence.original_filename,
            "original_sha256": evidence.original_sha256,
            "status": evidence.status,
        }}), 201
    except Exception:
        db.session.rollback()
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise


@evidence_bp.route("/evidence/<int:evidence_id>", methods=["GET"])
@login_required
def get_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    if not can_view_evidence(current_user, evidence):
        return jsonify({"error": "Unauthorized to access this evidence."}), 403
    return jsonify({"evidence": {
        "id": evidence.id,
        "case_id": evidence.case_id,
        "original_filename": evidence.original_filename,
        "stored_filename": evidence.stored_filename,
        "file_size": evidence.file_size,
        "file_type": evidence.file_type,
        "source_device": evidence.source_device,
        "acquisition_method": evidence.acquisition_method,
        "acquisition_timestamp": evidence.acquisition_timestamp.isoformat() if evidence.acquisition_timestamp else None,
        "acquiring_investigator_id": evidence.acquiring_investigator_id,
        "original_sha256": evidence.original_sha256,
        "current_custodian_id": evidence.current_custodian_id,
        "status": evidence.status,
        "storage_path": evidence.storage_path
    }})


@evidence_bp.route("/evidence/<int:evidence_id>/verify", methods=["POST"])
@login_required
def verify_evidence(evidence_id):
    if current_user.role.name not in {"Administrator", "Investigator", "Auditor"}:
        return jsonify({"error": "Unauthorized."}), 403

    evidence = Evidence.query.get_or_404(evidence_id)
    if not can_view_evidence(current_user, evidence):
        return jsonify({"error": "Unauthorized to verify this evidence."}), 403

    if not os.path.exists(evidence.storage_path):
        result = "VERIFICATION FAILED"
        calculated_hash = None
        audit = AuditLog(
            user_id=current_user.id,
            evidence_id=evidence.id,
            case_id=evidence.case_id,
            action_type="VERIFICATION_FAILED",
            description="Evidence file missing during verification.",
            details=str({"error": "missing_file"}),
        )
        db.session.add(audit)
        db.session.commit()
        return jsonify({"result": result, "evidence_id": evidence.id, "calculated_hash": None})

    try:
        with open(evidence.storage_path, "rb") as fh:
            digest = hashlib.sha256()
            for chunk in iter(lambda: fh.read(65536), b""):
                digest.update(chunk)
        calculated_hash = digest.hexdigest()
        result = "INTEGRITY VERIFIED" if calculated_hash == evidence.original_sha256 else "INTEGRITY MISMATCH"
    except Exception:
        result = "VERIFICATION FAILED"
        calculated_hash = None

    verification = EvidenceVerification(
        evidence_id=evidence.id,
        verified_by_id=current_user.id,
        original_hash=evidence.original_sha256,
        calculated_hash=calculated_hash,
        result=result,
        notes="Server-side verification performed.",
    )
    db.session.add(verification)

    audit = AuditLog(
        user_id=current_user.id,
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        action_type="INTEGRITY_VERIFIED" if result == "INTEGRITY VERIFIED" else "INTEGRITY_MISMATCH" if result == "INTEGRITY MISMATCH" else "VERIFICATION_FAILED",
        description=f"Integrity verification result: {result}",
        details=str({"original_hash": evidence.original_sha256, "calculated_hash": calculated_hash, "result": result}),
    )
    db.session.add(audit)
    db.session.commit()
    return jsonify({"result": result, "evidence_id": evidence.id, "original_hash": evidence.original_sha256, "calculated_hash": calculated_hash, "verified_by": current_user.id})


@evidence_bp.route("/evidence/<int:evidence_id>/download", methods=["GET"])
@login_required
def download_evidence(evidence_id):
    evidence = Evidence.query.get_or_404(evidence_id)
    if not can_view_evidence(current_user, evidence):
        return jsonify({"error": "Unauthorized to download this evidence."}), 403

    if not os.path.exists(evidence.storage_path):
        return jsonify({"error": "Evidence file is missing."}), 404

    audit = AuditLog(
        user_id=current_user.id,
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        action_type="EVIDENCE_DOWNLOADED",
        description=f"Evidence downloaded by {current_user.username}",
        details=str({"filename": evidence.original_filename}),
    )
    db.session.add(audit)
    db.session.commit()
    return send_file(evidence.storage_path, as_attachment=True, download_name=evidence.original_filename)
