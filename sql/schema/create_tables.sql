-- Student Success Analytics — Warehouse Schema
-- Star schema designed for institutional research analytics.
-- Portable: works on SQLite, SQL Server, PostgreSQL.

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_student (
    id_student INTEGER PRIMARY KEY,
    gender TEXT,
    region TEXT,
    highest_education TEXT,
    imd_band TEXT,                    -- socioeconomic index
    age_band TEXT,                    -- '0-35', '35-55', '55<='
    num_of_prev_attempts INTEGER,
    studied_credits INTEGER,
    disability TEXT,                  -- 'Yes' / 'No'
    enrollment_type TEXT             -- 'First-Time' / 'Returning'
);

-- ============================================================
-- FACT TABLES
-- ============================================================

-- One row per student × course × term
CREATE TABLE IF NOT EXISTS fact_enrollment (
    id_student INTEGER,
    code_module TEXT,
    code_presentation TEXT,
    date_registration INTEGER,
    final_result TEXT,               -- Pass, Fail, Withdrawn, Distinction
    final_grade TEXT,                 -- A, C, F, W
    grade_points REAL,               -- 4.0, 3.0, 1.0, 0.0
    passed INTEGER,                  -- 1 or 0
    withdrew INTEGER,                -- 1 or 0
    studied_credits INTEGER
);

-- Weekly LMS engagement aggregation
CREATE TABLE IF NOT EXISTS fact_weekly_engagement (
    id_student INTEGER,
    code_module TEXT,
    code_presentation TEXT,
    activity_week INTEGER,
    total_clicks INTEGER,
    sites_visited INTEGER,
    days_active INTEGER
);

-- Semester-to-semester retention tracking
CREATE TABLE IF NOT EXISTS fact_retention (
    id_student INTEGER PRIMARY KEY,
    cohort_term TEXT,
    terms_enrolled INTEGER,
    cumulative_gpa REAL,
    cumulative_credits INTEGER,
    is_graduated INTEGER,
    is_dropped_out INTEGER,
    retention_status TEXT            -- Retained, Graduated, At-Risk, Dropped Out
);

-- ETL audit log
CREATE TABLE IF NOT EXISTS etl_log (
    table_name TEXT,
    rows_loaded INTEGER,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
