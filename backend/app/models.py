from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from app import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="role")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    role = relationship("Role", back_populates="users")

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    case_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    incident_category = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.String(20), default="MEDIUM")
    status = db.Column(db.String(30), default="OPEN")
    assigned_investigator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    assigned_investigator = relationship("User", foreign_keys=[assigned_investigator_id])
    creator = relationship("User", foreign_keys=[created_by_id])


class CaseAssignment(db.Model):
    __tablename__ = "case_assignments"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("case_id", "user_id", name="uq_case_user"),)


class Evidence(db.Model):
    __tablename__ = "evidence"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    source_device = db.Column(db.String(255), nullable=True)
    acquisition_method = db.Column(db.String(100), nullable=False)
    acquisition_timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    acquiring_investigator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_sha256 = db.Column(db.String(128), nullable=False)
    current_custodian_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(30), default="REGISTERED")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    case = relationship("Case")
    acquirer = relationship("User", foreign_keys=[acquiring_investigator_id])
    custodian = relationship("User", foreign_keys=[current_custodian_id])


class EvidenceVerification(db.Model):
    __tablename__ = "evidence_verifications"

    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey("evidence.id"), nullable=False)
    verified_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_hash = db.Column(db.String(128), nullable=False)
    calculated_hash = db.Column(db.String(128), nullable=True)
    verification_timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    result = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class CustodyTransfer(db.Model):
    __tablename__ = "custody_transfers"

    id = db.Column(db.Integer, primary_key=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey("evidence.id"), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(30), default="PENDING")
    reason = db.Column(db.Text, default="")
    initiated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    accepted_at = db.Column(db.DateTime, nullable=True)
    previous_event_hash = db.Column(db.String(128), nullable=True)
    current_event_hash = db.Column(db.String(128), nullable=True)
    signature_status = db.Column(db.String(30), default="NOT_SIGNED")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    evidence_id = db.Column(db.Integer, db.ForeignKey("evidence.id"), nullable=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=True)
    action_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    details = db.Column(db.Text, default="{}")
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    previous_event_hash = db.Column(db.String(128), nullable=True)
    current_event_hash = db.Column(db.String(128), nullable=True)
    signature_status = db.Column(db.String(30), default="NOT_SIGNED")


class DigitalSignature(db.Model):
    __tablename__ = "digital_signatures"

    id = db.Column(db.Integer, primary_key=True)
    signer_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    public_key_id = db.Column(db.String(120), nullable=True)
    signature_value = db.Column(db.Text, nullable=False)
    signed_data_hash = db.Column(db.String(128), nullable=False)
    verification_status = db.Column(db.String(30), default="PENDING")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    verified_at = db.Column(db.DateTime, nullable=True)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    linked_record = db.Column(db.String(200), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ReportRecord(db.Model):
    __tablename__ = "report_records"

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.String(80), unique=True, nullable=False)
    generated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    report_path = db.Column(db.String(500), nullable=False)
    report_hash = db.Column(db.String(128), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# Seed roles
DEFAULT_ROLES = ["Administrator", "Investigator", "Auditor"]
