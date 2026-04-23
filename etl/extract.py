"""
Extract: Load raw OULAD CSV files into DataFrames.
Mirrors pulling from SIS + LMS at a real university.
"""
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'oulad')

EXPECTED_TABLES = [
    'courses', 'studentInfo', 'studentRegistration',
    'assessments', 'studentAssessment', 'vle', 'studentVle'
]


def load_all_tables():
    """Load all OULAD CSV tables into a dict of DataFrames."""
    tables = {}
    for table in EXPECTED_TABLES:
        filepath = os.path.join(DATA_DIR, f'{table}.csv')
        if not os.path.exists(filepath):
            print(f"  WARNING: {table}.csv not found, skipping")
            continue
        tables[table] = pd.read_csv(filepath)
        print(f"  Loaded {table}: {len(tables[table]):,} rows, {len(tables[table].columns)} columns")
    return tables


def validate_tables(tables):
    """Basic validation — check required columns exist."""
    checks = {
        'studentInfo': ['id_student', 'code_module', 'code_presentation', 'final_result'],
        'studentVle': ['id_student', 'code_module', 'date', 'sum_click'],
        'studentAssessment': ['id_student', 'id_assessment', 'score'],
        'assessments': ['id_assessment', 'code_module', 'assessment_type'],
    }
    issues = []
    for table_name, required_cols in checks.items():
        if table_name not in tables:
            issues.append(f"Missing table: {table_name}")
            continue
        missing = [c for c in required_cols if c not in tables[table_name].columns]
        if missing:
            issues.append(f"{table_name} missing columns: {missing}")

    if issues:
        print("\nValidation issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nAll tables validated successfully.")

    return len(issues) == 0


if __name__ == '__main__':
    print("Loading OULAD tables...")
    tables = load_all_tables()
    validate_tables(tables)
