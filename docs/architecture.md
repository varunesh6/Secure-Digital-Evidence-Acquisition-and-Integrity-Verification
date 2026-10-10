# System architecture

## High-level flow
1. Investigator authenticates into the system.
2. Investigator creates a case and registers evidence.
3. Server calculates a SHA-256 hash and stores the original file in protected storage.
4. Verification compares the live file bytes with the trusted original hash.
5. Custody transfer changes are tracked in a timeline and audit log.
6. Reports generate a PDF from real evidence and case records.

## Components
- Frontend React app for dashboards, case views, upload forms, and report access
- Flask API for authentication, permissions, upload processing, verification, and reporting
- SQLAlchemy models for persistence and relationships
- Protected file storage directory for original evidence files
- Audit and notification services for compliance trails

## Security model
- Password hashing via Werkzeug
- Role enforcement on backend routes
- File-type allowlist, secure filenames, and protected storage paths
- Hash verification on actual evidence bytes
- Digital signatures for signed manifests
- Audit logging for evidence access and changes
