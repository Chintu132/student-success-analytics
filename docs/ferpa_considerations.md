# FERPA & Data Privacy Design Notes

## What is FERPA?

The Family Educational Rights and Privacy Act (20 U.S.C. § 1232g) protects student education records at institutions receiving federal funding. Any analytics system at a university must be designed with FERPA in mind.

## How This Project Handles Privacy

### Data Used

This project uses ONLY publicly available datasets (OULAD, IPEDS). No actual student records from any institution are used. The OULAD dataset was released by The Open University under a CC-BY 4.0 license with pre-anonymized student identifiers.

### Design Principles (If Deployed at a Real University)

**1. De-identification**
Student IDs would be hashed (SHA-256) before loading into the analytics warehouse. No names, SSNs, email addresses, or contact information would exist in the analytical layer. Only the source SIS retains PII.

**2. Minimum Necessary Standard**
Dashboards display aggregate metrics only by default. Drill-down to individual student records requires authenticated role-based access and is logged.

**3. Row-Level Security (RLS)**
Power BI dashboards would enforce RLS so that department chairs see only their department's courses, academic advisors see only their assigned students, deans see their college, and the provost/IR office sees institution-wide data.

**4. Aggregation Suppression**
Any reporting cell with fewer than 10 students is suppressed to prevent re-identification. This follows standard NCES (National Center for Education Statistics) reporting practice.

**5. Audit Trail**
All queries against student-level data are logged with user ID, timestamp, and query purpose. Logs are retained for 3 years per institutional policy.

**6. Data Retention**
Raw clickstream data is aged out after 3 years. Aggregated metrics are retained indefinitely for trend analysis. Individual assessment scores are retained for the duration of enrollment plus 5 years.

**7. Directory Information Exception**
Only FERPA-designated directory information (name, enrollment status, degree) may be disclosed without consent. All analytics in this system operate on non-directory education records and require legitimate educational interest.

## Applicable Regulations

- **FERPA** (20 U.S.C. § 1232g) — Student education record privacy
- **HIPAA** — If health center data is integrated (not in scope here)
- **USG BOR Policy 10.1** — University System of Georgia data governance
- **SACSCOC Standard 10.5** — Accreditation requirements for institutional research
