"""
Run the full ETL pipeline: Extract → Transform → Load.
"""
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from etl.extract import load_all_tables, validate_tables
from etl.transform import (
    transform_students,
    transform_enrollments,
    transform_vle_engagement,
    transform_retention,
)
from etl.load import load_all


def run():
    start = time.time()
    print("=" * 60)
    print("STUDENT SUCCESS ANALYTICS — ETL PIPELINE")
    print("=" * 60)

    # --- EXTRACT ---
    print("\n[1/3] EXTRACT — Loading raw OULAD data...")
    tables = load_all_tables()
    if not validate_tables(tables):
        print("Validation failed. Run download_oulad.py first.")
        sys.exit(1)

    # --- TRANSFORM ---
    print("\n[2/3] TRANSFORM — Cleaning and building features...")
    students = transform_students(tables['studentInfo'])
    enrollments = transform_enrollments(tables['studentInfo'])
    engagement = transform_vle_engagement(tables['studentVle'])
    retention = transform_retention(tables['studentInfo'])

    # --- LOAD ---
    print("\n[3/3] LOAD — Populating warehouse...")
    load_all(students, enrollments, engagement, retention)

    elapsed = time.time() - start
    print(f"\nPipeline completed in {elapsed:.1f} seconds.")
    print("=" * 60)


if __name__ == '__main__':
    run()
