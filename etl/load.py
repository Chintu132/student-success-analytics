"""
Load: Populate SQLite warehouse with transformed data.
SQLite used for portability — same SQL patterns work on SQL Server/PostgreSQL.
"""
import sqlite3
import pandas as pd
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_schema(conn):
    """Create dimensional model tables."""
    schema_sql = """
    DROP TABLE IF EXISTS dim_student;
    CREATE TABLE dim_student (
        id_student INTEGER PRIMARY KEY,
        gender TEXT,
        region TEXT,
        highest_education TEXT,
        imd_band TEXT,
        age_band TEXT,
        num_of_prev_attempts INTEGER,
        studied_credits INTEGER,
        disability TEXT,
        enrollment_type TEXT
    );

    DROP TABLE IF EXISTS fact_enrollment;
    CREATE TABLE fact_enrollment (
        id_student INTEGER,
        code_module TEXT,
        code_presentation TEXT,
        date_registration INTEGER,
        final_result TEXT,
        final_grade TEXT,
        grade_points REAL,
        passed INTEGER,
        withdrew INTEGER,
        studied_credits INTEGER
    );

    DROP TABLE IF EXISTS fact_weekly_engagement;
    CREATE TABLE fact_weekly_engagement (
        id_student INTEGER,
        code_module TEXT,
        code_presentation TEXT,
        activity_week INTEGER,
        total_clicks INTEGER,
        sites_visited INTEGER,
        days_active INTEGER
    );

    DROP TABLE IF EXISTS fact_retention;
    CREATE TABLE fact_retention (
        id_student INTEGER PRIMARY KEY,
        cohort_term TEXT,
        terms_enrolled INTEGER,
        cumulative_gpa REAL,
        cumulative_credits INTEGER,
        is_graduated INTEGER,
        is_dropped_out INTEGER,
        retention_status TEXT
    );

    DROP TABLE IF EXISTS etl_log;
    CREATE TABLE etl_log (
        table_name TEXT,
        rows_loaded INTEGER,
        loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    conn.executescript(schema_sql)
    print("  Schema created.")


def load_table(conn, df, table_name):
    """Load a DataFrame into the warehouse with logging."""
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.execute(
        "INSERT INTO etl_log (table_name, rows_loaded) VALUES (?, ?)",
        (table_name, len(df))
    )
    conn.commit()
    print(f"  Loaded {table_name}: {len(df):,} rows")


def load_all(students_df, enrollments_df, engagement_df, retention_df):
    """Load all transformed tables into the warehouse."""
    conn = get_connection()
    create_schema(conn)
    load_table(conn, students_df, 'dim_student')
    load_table(conn, enrollments_df, 'fact_enrollment')
    load_table(conn, engagement_df, 'fact_weekly_engagement')
    load_table(conn, retention_df, 'fact_retention')

    # Print summary
    cursor = conn.execute("SELECT table_name, rows_loaded, loaded_at FROM etl_log")
    print("\n  ETL Log:")
    for row in cursor:
        print(f"    {row[0]}: {row[1]:,} rows at {row[2]}")

    conn.close()
    print(f"\n  Warehouse saved to {DB_PATH}")


if __name__ == '__main__':
    print("Run this through run_pipeline.py")
