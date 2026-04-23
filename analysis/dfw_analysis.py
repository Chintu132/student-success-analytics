"""
DFW Rate Analysis (D/F/Withdraw)
================================
Identifies "barrier courses" — courses where students disproportionately
earn D grades, fail, or withdraw. Used by IR offices and provosts to
target interventions (tutoring, redesign, support services).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlite3


def load_data():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')
    conn = sqlite3.connect(db_path)
    enrollment = pd.read_sql("SELECT * FROM fact_enrollment", conn)
    conn.close()
    return enrollment


def calculate_dfw_rates(enrollment_df):
    """
    Calculate DFW rate by course.
    DFW = (D + F + W) / Total Enrolled * 100
    In OULAD terms: Fail + Withdrawn vs Pass + Distinction
    """
    df = enrollment_df.copy()

    # DFW flag
    df['is_dfw'] = df['final_result'].isin(['Fail', 'Withdrawn']).astype(int)
    df['is_withdraw'] = (df['final_result'] == 'Withdrawn').astype(int)
    df['is_fail'] = (df['final_result'] == 'Fail').astype(int)

    course_stats = (df
        .groupby(['code_module', 'code_presentation'])
        .agg(
            total_enrolled=('id_student', 'nunique'),
            dfw_count=('is_dfw', 'sum'),
            fail_count=('is_fail', 'sum'),
            withdraw_count=('is_withdraw', 'sum'),
            pass_count=('passed', 'sum'),
            avg_grade_points=('grade_points', 'mean'),
        )
        .reset_index()
    )

    course_stats['dfw_rate'] = (course_stats['dfw_count'] / course_stats['total_enrolled'] * 100).round(1)
    course_stats['fail_rate'] = (course_stats['fail_count'] / course_stats['total_enrolled'] * 100).round(1)
    course_stats['withdraw_rate'] = (course_stats['withdraw_count'] / course_stats['total_enrolled'] * 100).round(1)
    course_stats['avg_grade_points'] = course_stats['avg_grade_points'].round(2)

    # Flag barrier courses (DFW > 40%)
    course_stats['is_barrier'] = (course_stats['dfw_rate'] > 40).astype(int)

    return course_stats.sort_values('dfw_rate', ascending=False)


def calculate_dfw_by_demographics(enrollment_df, students_df=None):
    """
    DFW rates broken out by demographic groups.
    Identifies equity gaps in course outcomes.
    """
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')
    conn = sqlite3.connect(db_path)
    students = pd.read_sql("SELECT * FROM dim_student", conn)
    conn.close()

    df = enrollment_df.merge(students, on='id_student', how='left')
    df['is_dfw'] = df['final_result'].isin(['Fail', 'Withdrawn']).astype(int)

    # By age band
    age_dfw = (df
        .groupby('age_band')
        .agg(total=('id_student', 'count'), dfw=('is_dfw', 'sum'))
        .reset_index()
    )
    age_dfw['dfw_rate'] = (age_dfw['dfw'] / age_dfw['total'] * 100).round(1)

    # By education level
    edu_dfw = (df
        .groupby('highest_education')
        .agg(total=('id_student', 'count'), dfw=('is_dfw', 'sum'))
        .reset_index()
    )
    edu_dfw['dfw_rate'] = (edu_dfw['dfw'] / edu_dfw['total'] * 100).round(1)

    # By disability status
    dis_dfw = (df
        .groupby('disability')
        .agg(total=('id_student', 'count'), dfw=('is_dfw', 'sum'))
        .reset_index()
    )
    dis_dfw['dfw_rate'] = (dis_dfw['dfw'] / dis_dfw['total'] * 100).round(1)

    return age_dfw, edu_dfw, dis_dfw


def plot_dfw_by_course(course_stats, output_dir):
    """Bar chart of DFW rates by course module."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Aggregate to module level
    module_stats = (course_stats
        .groupby('code_module')
        .agg(
            avg_dfw_rate=('dfw_rate', 'mean'),
            total_enrolled=('total_enrolled', 'sum'),
        )
        .reset_index()
        .sort_values('avg_dfw_rate', ascending=True)
    )

    colors = ['#d7191c' if r > 40 else '#fdae61' if r > 30 else '#1a9641'
              for r in module_stats['avg_dfw_rate']]

    bars = ax.barh(module_stats['code_module'], module_stats['avg_dfw_rate'], color=colors)
    ax.axvline(x=40, color='red', linestyle='--', alpha=0.5, label='Barrier threshold (40%)')
    ax.axvline(x=30, color='orange', linestyle='--', alpha=0.5, label='Warning threshold (30%)')

    # Add enrollment count labels
    for bar, enrolled in zip(bars, module_stats['total_enrolled']):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'n={enrolled:,}', va='center', fontsize=9)

    ax.set_xlabel('DFW Rate (%)', fontsize=12)
    ax.set_ylabel('Course Module', fontsize=12)
    ax.set_title('DFW Rates by Course — Identifying Barrier Courses', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'dfw_by_course.png')
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"  Chart saved: {filepath}")


def plot_dfw_equity_gaps(age_dfw, edu_dfw, output_dir):
    """Side-by-side equity gap charts."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # By age
    age_sorted = age_dfw.sort_values('dfw_rate')
    ax1.barh(age_sorted['age_band'], age_sorted['dfw_rate'], color='#0066CC')
    ax1.set_xlabel('DFW Rate (%)')
    ax1.set_title('DFW Rate by Age Band', fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')

    # By education
    edu_sorted = edu_dfw.sort_values('dfw_rate')
    ax2.barh(edu_sorted['highest_education'], edu_sorted['dfw_rate'], color='#CC6633')
    ax2.set_xlabel('DFW Rate (%)')
    ax2.set_title('DFW Rate by Prior Education', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')

    plt.suptitle('Equity Gaps in Student Outcomes', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'dfw_equity_gaps.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Chart saved: {filepath}")


if __name__ == '__main__':
    print("=" * 60)
    print("DFW RATE ANALYSIS — BARRIER COURSE IDENTIFICATION")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'dashboards', 'screenshots')
    os.makedirs(output_dir, exist_ok=True)

    enrollment = load_data()
    print(f"\nLoaded {len(enrollment):,} enrollment records")

    # DFW by course
    print("\nDFW Rates by Course:")
    course_stats = calculate_dfw_rates(enrollment)
    print(course_stats[['code_module', 'code_presentation', 'total_enrolled',
                         'dfw_rate', 'fail_rate', 'withdraw_rate', 'is_barrier']].to_string(index=False))

    barrier_count = course_stats['is_barrier'].sum()
    print(f"\nBarrier courses (DFW > 40%): {barrier_count} out of {len(course_stats)}")

    # Equity gaps
    print("\nEquity Gap Analysis:")
    age_dfw, edu_dfw, dis_dfw = calculate_dfw_by_demographics(enrollment)
    print("\nBy Age Band:")
    print(age_dfw.to_string(index=False))
    print("\nBy Prior Education:")
    print(edu_dfw.to_string(index=False))
    print("\nBy Disability Status:")
    print(dis_dfw.to_string(index=False))

    # Charts
    print("\nGenerating charts...")
    plot_dfw_by_course(course_stats, output_dir)
    plot_dfw_equity_gaps(age_dfw, edu_dfw, output_dir)

    print("\nDone.")
