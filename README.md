# Secure Digital Evidence Acquisition and Integrity Verification System

## Overview
This project is a Flask + React web application for managing cybercrime investigation evidence intake, preserving original files, verifying SHA-256 integrity, tracking custody changes, generating signed audit records, and producing PDF reports.

## Architecture
- Frontend: React + Vite + Tailwind CSS + Recharts
- Backend: Flask + Flask-SQLAlchemy + Flask-Migrate + Flask-Login
- Database: SQLite for local development, with MySQL-ready configuration support
- Evidence storage: protected local file storage under `backend/storage/evidence`
- Reporting: ReportLab PDF generation
- Security: password hashing, role-based authorization, audit logs, file-type checks, and protected evidence access

## Folder structure
- `backend/` — Flask app, models, routes, services, security helpers, config, and migrations
- `frontend/` — React frontend and UI pages
- `tests/` — backend validation and workflow tests
- `docs/` — architecture and use-case docs
- `.env.example` — environment template
- `requirements.txt` — Python dependencies
- `package.json` — frontend dependencies

## Database design
Core tables include:
- `users`
- `roles`
- `cases`
- `case_assignments`
- `evidence`
- `evidence_verifications`
- `custody_transfers`
- `audit_logs`
- `digital_signatures`
- `notifications`
- `report_records`

## Local setup
1. Create a virtual environment:
   `python -m venv .venv`
2. Activate it:
   `\.venv\Scripts\activate`
3. Install Python packages:
   `python -m pip install -r requirements.txt`
4. Install frontend dependencies:
   `cd frontend && npm install`
5. Copy `.env.example` to `.env` and update values if needed.

## Startup commands
Backend:
`cd backend && ..\.venv\Scripts\python.exe run.py`

Frontend:
`cd frontend && npm run dev`

## Admin setup
Create an administrator via the API:
`POST /api/auth/setup-admin`
Example JSON:
{
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "System Admin",
  "password": "StrongPassword123!"
}

## Important notes
- Evidence originals are kept in restricted local storage.
- Hash mismatches do not overwrite the original trusted hash.
- Digital signatures are used for record signing and verification, not as a replacement for hashing.
- This is a demonstration-safe evidence management system and should be adapted for real forensic workflows with stronger key management and access controls.

## Testing
Run backend tests:
`cd backend && ..\.venv\Scripts\python.exe -m pytest ../tests/test_core_workflows.py -q`

Expected result: all critical workflow tests pass.
