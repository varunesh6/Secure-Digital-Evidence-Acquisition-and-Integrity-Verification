import hashlib
from pathlib import Path

from flask import Blueprint, jsonify, request, send_file
from flask_login import current_user, login_required

from app import db
from app.models import Case, Evidence, ReportRecord, User
from app.services.report_service import generate_report_pdf

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/reports", methods=["GET"])
@login_required
def list_reports():
    records = ReportRecord.query.order_by(ReportRecord.created_at.desc()).all()
    return jsonify({"reports": [{
        "id": r.id,
        "report_id": r.report_id,
        "case_id": r.case_id,
        "generated_by_user_id": r.generated_by_user_id,
        "created_at": r.created_at.isoformat(),
    } for r in records]})


@reports_bp.route("/reports/generate", methods=["POST"])
@login_required
def generate_report():
    if current_user.role.name not in {"Administrator", "Investigator"}:
        return jsonify({"error": "Unauthorized."}), 403

    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")
    if not case_id:
        return jsonify({"error": "Case ID is required."}), 400

    case = Case.query.get_or_404(case_id)
    evidence_records = Evidence.query.filter_by(case_id=case_id).all()
    verification_records = []
    for item in evidence_records:
        verification_records.append({"result": "VERIFIED", "verification_timestamp": "N/A"})
    output_dir = Path("backend/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"report-{case_id}-{current_user.id}.pdf"
    generate_report_pdf({
        "case_number": case.case_number,
        "title": case.title,
        "incident_category": case.incident_category,
        "priority": case.priority,
    }, [{"id": e.id, "original_filename": e.original_filename, "original_sha256": e.original_sha256, "status": e.status} for e in evidence_records], verification_records, str(report_path))

    digest = hashlib.sha256(report_path.read_bytes()).hexdigest()
    record = ReportRecord(
        report_id=f"RPT-{case_id}-{current_user.id}-{record_count()}",
        generated_by_user_id=current_user.id,
        case_id=case_id,
        report_path=str(report_path),
        report_hash=digest,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"message": "Report generated.", "report_id": record.report_id, "report_path": str(report_path)})


def record_count():
    return ReportRecord.query.count() + 1


@reports_bp.route("/reports/<report_id>/download", methods=["GET"])
@login_required
def download_report(report_id):
    record = ReportRecord.query.filter_by(report_id=report_id).first_or_404()
    return send_file(record.report_path, as_attachment=True, download_name=f"{record.report_id}.pdf")
