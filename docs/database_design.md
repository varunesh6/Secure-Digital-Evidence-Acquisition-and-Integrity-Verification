# Database design

## Tables
- `roles`: Role metadata
- `users`: Investigator, auditor, and admin credentials and profile data
- `cases`: Investigation records and status metadata
- `case_assignments`: User-to-case assignments
- `evidence`: Original evidence registration details and protected file references
- `evidence_verifications`: Integrity verification attempts and results
- `custody_transfers`: Transfer lifecycle and recipient updates
- `audit_logs`: Security and access events
- `digital_signatures`: Signed statement records and public key identifiers
- `notifications`: In-app notifications for the user
- `report_records`: Generated PDF report references

## Notes
- Use database transactions for multi-step updates like custody acceptance.
- Keep original file hash separate from verification results.
- Keep the evidence original in protected storage and restrict user access.
- Append-only behavior is enforced by permissions and operational controls, not by assuming a database can never be tampered with.
