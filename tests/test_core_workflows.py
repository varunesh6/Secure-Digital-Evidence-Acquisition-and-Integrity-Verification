import hashlib
import io
from pathlib import Path

import pytest

from app import create_app, db
from app.models import AuditLog, Case, CustodyTransfer, Evidence, Role, User
from app.security.signing_service import ensure_key_pair, sign_payload, verify_signature
from werkzeug.security import generate_password_hash


@pytest.fixture
def app_client():
    app = create_app('testing')
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin_role = Role(name='Administrator', description='Admin')
        investigator_role = Role(name='Investigator', description='Investigator')
        auditor_role = Role(name='Auditor', description='Auditor')
        db.session.add_all([admin_role, investigator_role, auditor_role])
        db.session.commit()

        admin_user = User(username='admin', email='admin@example.com', full_name='System Admin', password_hash=generate_password_hash('admin123'), role_id=admin_role.id, is_active=True)
        investigator = User(username='investigator', email='inv@example.com', full_name='Case Investigator', password_hash=generate_password_hash('inv123'), role_id=investigator_role.id, is_active=True)
        auditor = User(username='auditor', email='audit@example.com', full_name='Compliance Auditor', password_hash=generate_password_hash('aud123'), role_id=auditor_role.id, is_active=True)
        db.session.add_all([admin_user, investigator, auditor])
        db.session.commit()

        case = Case(
            case_number='CASE-0001',
            title='Phishing campaign',
            description='Malware investigation',
            incident_category='Cybercrime',
            priority='HIGH',
            status='OPEN',
            assigned_investigator_id=investigator.id,
            created_by_id=investigator.id,
            notes='Initial triage.'
        )
        db.session.add(case)
        db.session.commit()

        evidence_file = io.BytesIO(b'origin content for evidence')
        evidence_file.name = 'sample.txt'
        storage_dir = Path(app.config['EVIDENCE_STORAGE_PATH'])
        storage_dir.mkdir(parents=True, exist_ok=True)
        file_path = storage_dir / 'original_sample.txt'
        file_path.write_bytes(b'origin content for evidence')
        actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        evidence = Evidence(
            case_id=case.id,
            original_filename='sample.txt',
            stored_filename='original_sample.txt',
            storage_path=str(file_path),
            file_size=file_path.stat().st_size,
            file_type='txt',
            source_device='Laptop',
            acquisition_method='FILE_UPLOAD',
            acquiring_investigator_id=investigator.id,
            original_sha256=actual_hash,
            current_custodian_id=investigator.id,
            status='REGISTERED',
        )
        db.session.add(evidence)
        db.session.commit()

        client = app.test_client()
        yield client, app, investigator, auditor, case, evidence


def test_login_and_authorization(app_client):
    client, _, _, _, _, _ = app_client
    response = client.post('/api/auth/login', json={'username': 'investigator', 'password': 'inv123'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['user']['username'] == 'investigator'

    unauthorized = client.get('/api/cases')
    assert unauthorized.status_code in (200, 403)


def test_case_creation_and_evidence_upload(app_client):
    client, app, investigator, _, case, _ = app_client
    login = client.post('/api/auth/login', json={'username': 'investigator', 'password': 'inv123'})
    assert login.status_code == 200

    case_response = client.post('/api/cases', json={'title': 'Ransomware investigation', 'incident_category': 'Malware', 'priority': 'HIGH', 'status': 'OPEN', 'notes': 'Test case'})
    assert case_response.status_code == 201
    created_case = case_response.get_json()['case']
    assert created_case['title'] == 'Ransomware investigation'

    file_data = (io.BytesIO(b'This is a test evidence file.'), 'test_evidence.txt')
    upload_response = client.post('/api/evidence/upload', data={'file': file_data, 'case_id': str(case.id), 'source_device': 'Demo laptop', 'acquisition_method': 'FILE_UPLOAD'}, content_type='multipart/form-data')
    assert upload_response.status_code == 201
    uploaded = upload_response.get_json()['evidence']
    assert uploaded['original_filename'] == 'test_evidence.txt'


def test_successful_verification_and_mismatch_detection(app_client):
    client, app, investigator, _, _, evidence = app_client
    client.post('/api/auth/login', json={'username': 'investigator', 'password': 'inv123'})

    success = client.post(f'/api/evidence/{evidence.id}/verify')
    assert success.status_code == 200
    assert success.get_json()['result'] == 'INTEGRITY VERIFIED'

    original_path = Path(evidence.storage_path)
    tampered_path = original_path.with_name('tampered_copy.txt')
    tampered_path.write_bytes(b'changed bytes for mismatch')
    evidence.storage_path = str(tampered_path)
    db.session.commit()

    mismatch = client.post(f'/api/evidence/{evidence.id}/verify')
    assert mismatch.status_code == 200
    assert mismatch.get_json()['result'] == 'INTEGRITY MISMATCH'


def test_unauthorized_evidence_access(app_client):
    client, _, _, auditor, _, evidence = app_client
    client.post('/api/auth/login', json={'username': 'auditor', 'password': 'aud123'})
    response = client.get(f'/api/evidence/{evidence.id}')
    assert response.status_code == 200

    new_user = User(username='newuser', email='newuser@example.com', full_name='Guest User', password_hash=generate_password_hash('guest123'), role_id=Role.query.filter_by(name='Investigator').first().id, is_active=True)
    db.session.add(new_user)
    db.session.commit()
    client.post('/api/auth/logout')
    login = client.post('/api/auth/login', json={'username': 'newuser', 'password': 'guest123'})
    assert login.status_code == 200
    access = client.get(f'/api/evidence/{evidence.id}')
    assert access.status_code == 403


def test_custody_transfer_and_acceptance(app_client):
    client, _, investigator, auditor, _, evidence = app_client
    client.post('/api/auth/login', json={'username': 'investigator', 'password': 'inv123'})
    transfer = client.post('/api/custody/transfer', json={'evidence_id': evidence.id, 'to_user_id': auditor.id, 'reason': 'For review'})
    assert transfer.status_code == 200
    transfer_id = transfer.get_json()['transfer_id']

    client.post('/api/auth/logout')
    client.post('/api/auth/login', json={'username': 'auditor', 'password': 'aud123'})
    accepted = client.post(f'/api/custody/{transfer_id}/accept')
    assert accepted.status_code == 200
    assert accepted.get_json()['message'] == 'Custody transfer accepted.'


def test_audit_log_and_signature_generation(app_client):
    client, _, _, _, _, evidence = app_client
    audit = AuditLog(
        user_id=1,
        evidence_id=evidence.id,
        case_id=evidence.case_id,
        action_type='SIGNATURE_CHECK',
        description='Signed evidence manifest checked',
        details='{"status": "signed"}'
    )
    db.session.add(audit)
    db.session.commit()
    assert AuditLog.query.filter_by(action_type='SIGNATURE_CHECK').count() == 1

    key_dir = Path('test_keys')
    priv_path, pub_path = ensure_key_pair(str(key_dir))
    payload = {'entity_type': 'audit_log', 'entity_id': str(audit.id)}
    signature = sign_payload(payload, priv_path)
    assert verify_signature(payload, signature, pub_path) is True


def test_report_generation(app_client):
    client, _, investigator, _, case, _ = app_client
    client.post('/api/auth/login', json={'username': 'investigator', 'password': 'inv123'})
    report = client.post('/api/reports/generate', json={'case_id': case.id})
    assert report.status_code == 200
    assert 'report_id' in report.get_json()
