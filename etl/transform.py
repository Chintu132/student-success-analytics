"""
Transform: Clean, conform, and build analytical features from raw OULAD data.
"""
import pandas as pd
import numpy as np


def transform_students(student_info_df):
    """
    Clean studentInfo → dim_student format.
    Deduplicates to one row per student (keeping latest term).
    """
    df = student_info_df.copy()

    # Deduplicate — keep latest presentation per student
    df = (df
        .sort_values('code_presentation')
        .drop_duplicates(subset=['id_student'], keep='last')
    )

    # Standardize fields
    df['enrollment_type'] = df['num_of_prev_attempts'].apply(
        lambda x: 'First-Time' if x == 0 else 'Returning'
    )
    df['disability'] = df['disability'].map({'Y': 'Yes', 'N': 'No'}).fillna('Unknown')
    df['age_band'] = df['age_band'].fillna('Unknown')
    df['highest_education'] = df['highest_education'].fillna('Unknown')
    df['imd_band'] = df['imd_band'].fillna('Unknown')
    df['region'] = df['region'].fillna('Unknown')

    keep_cols = ['id_student', 'gender', 'region', 'highest_education',
                 'imd_band', 'age_band', 'num_of_prev_attempts',
                 'studied_credits', 'disability', 'enrollment_type']

    result = df[keep_cols].copy()
    print(f"  dim_student: {len(result):,} unique students")
    return result


def transform_enrollments(student_info_df):
    """
    Build fact_enrollment from studentInfo (one row per student × course × term).
    """
    df = student_info_df.copy()

    # Map final_result to grade-like fields
    df['passed'] = df['final_result'].isin(['Pass', 'Distinction']).astype(int)
    df['withdrew'] = (df['final_result'] == 'Withdrawn').astype(int)
    df['grade_points'] = df['final_result'].map({
        'Distinction': 4.0, 'Pass': 3.0, 'Fail': 1.0, 'Withdrawn': 0.0
    }).fillna(0.0)
    df['final_grade'] = df['final_result'].map({
        'Distinction': 'A', 'Pass': 'C', 'Fail': 'F', 'Withdrawn': 'W'
    }).fillna('W')

    keep_cols = ['id_student', 'code_module', 'code_presentation',
                 'date_registration', 'final_result', 'final_grade',
                 'grade_points', 'passed', 'withdrew', 'studied_credits']

    result = df[keep_cols].copy()
    print(f"  fact_enrollment: {len(result):,} rows")
    return result


def transform_vle_engagement(student_vle_df):
    """
    Aggregate VLE clickstream into weekly engagement metrics per student per course.
    Mirrors how a university would aggregate Canvas/Blackboard logs.
    """
    df = student_vle_df.copy()

    # Calculate week number from day offset
    df['activity_week'] = (df['date'] // 7) + 1

    # Aggregate by student × course × week
    weekly = (df
        .groupby(['id_student', 'code_module', 'code_presentation', 'activity_week'])
        .agg(
            total_clicks=('sum_click', 'sum'),
            sites_visited=('id_site', 'nunique'),
            days_active=('date', 'nunique'),
        )
        .reset_index()
    )

    print(f"  weekly_engagement: {len(weekly):,} rows")
    return weekly


def transform_retention(student_info_df):
    """
    Build retention tracking table.
    Identifies each student's cohort (first term) and tracks presence in subsequent terms.
    """
    df = student_info_df.copy()

    # Identify cohort term (first appearance)
    cohort = (df
        .groupby('id_student')['code_presentation']
        .min()
        .reset_index()
        .rename(columns={'code_presentation': 'cohort_term'})
    )

    # Get all terms each student appeared in
    terms_enrolled = (df
        .groupby('id_student')['code_presentation']
        .apply(set)
        .reset_index()
        .rename(columns={'code_presentation': 'terms'})
    )

    # Cumulative GPA
    df['grade_points'] = df['final_result'].map({
        'Distinction': 4.0, 'Pass': 3.0, 'Fail': 1.0, 'Withdrawn': 0.0
    }).fillna(0.0)
    cum_gpa = (df
        .groupby('id_student')['grade_points']
        .mean()
        .reset_index()
        .rename(columns={'grade_points': 'cumulative_gpa'})
    )

    # Cumulative credits
    cum_credits = (df
        .groupby('id_student')['studied_credits']
        .sum()
        .reset_index()
        .rename(columns={'studied_credits': 'cumulative_credits'})
    )

    # Latest outcome
    latest = (df
        .sort_values('code_presentation')
        .drop_duplicates(subset=['id_student'], keep='last')
        [['id_student', 'final_result']]
    )

    # Merge everything
    retention = (cohort
        .merge(terms_enrolled, on='id_student')
        .merge(cum_gpa, on='id_student')
        .merge(cum_credits, on='id_student')
        .merge(latest, on='id_student')
    )

    retention['terms_enrolled'] = retention['terms'].apply(len)
    retention['is_graduated'] = (retention['final_result'] == 'Distinction').astype(int)
    retention['is_dropped_out'] = (retention['final_result'] == 'Withdrawn').astype(int)

    retention['retention_status'] = retention['final_result'].map({
        'Pass': 'Retained', 'Distinction': 'Graduated',
        'Fail': 'At-Risk', 'Withdrawn': 'Dropped Out'
    })

    result = retention[['id_student', 'cohort_term', 'terms_enrolled',
                         'cumulative_gpa', 'cumulative_credits',
                         'is_graduated', 'is_dropped_out', 'retention_status']].copy()
    result['cumulative_gpa'] = result['cumulative_gpa'].round(3)

    print(f"  fact_retention: {len(result):,} rows")
    return result


if __name__ == '__main__':
    from extract import load_all_tables
    tables = load_all_tables()

    students = transform_students(tables['studentInfo'])
    enrollments = transform_enrollments(tables['studentInfo'])
    engagement = transform_vle_engagement(tables['studentVle'])
    retention = transform_retention(tables['studentInfo'])
