"""
LMS Engagement Scoring
======================
Builds a composite engagement score per student per course based on
their VLE/LMS activity patterns. Students scoring below 40 are flagged AT-RISK.

This is exactly what AU's online learning analytics team would build
to support student success interventions.
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
    engagement = pd.read_sql("SELECT * FROM fact_weekly_engagement", conn)
    enrollment = pd.read_sql("SELECT * FROM fact_enrollment", conn)
    conn.close()
    return engagement, enrollment


def calculate_engagement_score(engagement_df):
    """
    Build a composite engagement score per student per course.

    Components (weighted):
    - Click volume percentile within course — 40%
    - Activity consistency (% of weeks active) — 40%
    - Site diversity (breadth of VLE usage) — 20%

    Score: 0 to 100. Below 40 = AT-RISK.
    """
    # Aggregate across all weeks for each student-course
    student_course = (engagement_df
        .groupby(['id_student', 'code_module', 'code_presentation'])
        .agg(
            total_clicks=('total_clicks', 'sum'),
            total_sites=('sites_visited', 'sum'),
            avg_days_active=('days_active', 'mean'),
            weeks_active=('activity_week', 'nunique'),
            max_week=('activity_week', 'max'),
        )
        .reset_index()
    )

    # Click volume percentile within each course
    student_course['click_percentile'] = (
        student_course
        .groupby(['code_module', 'code_presentation'])['total_clicks']
        .rank(pct=True) * 100
    )

    # Consistency: what % of weeks did they show up?
    student_course['consistency'] = (
        student_course['weeks_active'] / student_course['max_week'].clip(lower=1) * 100
    ).clip(0, 100)

    # Site diversity percentile
    student_course['diversity_percentile'] = (
        student_course
        .groupby(['code_module', 'code_presentation'])['total_sites']
        .rank(pct=True) * 100
    )

    # Composite score
    student_course['engagement_score'] = (
        student_course['click_percentile'] * 0.40 +
        student_course['consistency'] * 0.40 +
        student_course['diversity_percentile'] * 0.20
    ).clip(0, 100).round(1)

    # Risk flag
    student_course['risk_flag'] = np.where(
        student_course['engagement_score'] < 40, 'AT-RISK',
        np.where(student_course['engagement_score'] < 60, 'WATCH', 'ON-TRACK')
    )

    return student_course


def analyze_engagement_vs_outcomes(scores_df, enrollment_df):
    """
    Correlate engagement scores with actual student outcomes.
    This proves the score is predictive.
    """
    merged = scores_df.merge(
        enrollment_df[['id_student', 'code_module', 'code_presentation', 'final_result', 'passed']],
        on=['id_student', 'code_module', 'code_presentation'],
        how='inner'
    )

    summary = (merged
        .groupby('risk_flag')
        .agg(
            students=('id_student', 'nunique'),
            avg_score=('engagement_score', 'mean'),
            pass_rate=('passed', 'mean'),
        )
        .reset_index()
    )
    summary['pass_rate'] = (summary['pass_rate'] * 100).round(1)
    summary['avg_score'] = summary['avg_score'].round(1)

    return summary, merged


def plot_engagement_distribution(scores_df, output_dir):
    """Histogram of engagement scores with risk zones."""
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(scores_df['engagement_score'], bins=50, color='#0066CC', alpha=0.7, edgecolor='white')
    ax.axvline(x=40, color='red', linestyle='--', linewidth=2, label='AT-RISK threshold (40)')
    ax.axvline(x=60, color='orange', linestyle='--', linewidth=2, label='WATCH threshold (60)')

    ax.set_xlabel('Engagement Score', fontsize=12)
    ax.set_ylabel('Number of Students', fontsize=12)
    ax.set_title('LMS Engagement Score Distribution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'engagement_distribution.png')
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"  Chart saved: {filepath}")


def plot_engagement_vs_outcome(merged_df, output_dir):
    """Box plot: engagement score by outcome."""
    fig, ax = plt.subplots(figsize=(10, 6))

    order = ['Distinction', 'Pass', 'Fail', 'Withdrawn']
    present = [o for o in order if o in merged_df['final_result'].unique()]
    colors = ['#1a9641', '#a6d96a', '#fdae61', '#d7191c']

    data_to_plot = [merged_df[merged_df['final_result'] == o]['engagement_score'] for o in present]
    bp = ax.boxplot(data_to_plot, labels=present, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors[:len(present)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel('Engagement Score', fontsize=12)
    ax.set_xlabel('Final Outcome', fontsize=12)
    ax.set_title('Engagement Score by Student Outcome', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'engagement_vs_outcome.png')
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"  Chart saved: {filepath}")


if __name__ == '__main__':
    print("=" * 60)
    print("LMS ENGAGEMENT SCORING")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'dashboards', 'screenshots')
    os.makedirs(output_dir, exist_ok=True)

    engagement, enrollment = load_data()
    print(f"\nLoaded {len(engagement):,} weekly engagement records")

    # Calculate scores
    print("\nCalculating engagement scores...")
    scores = calculate_engagement_score(engagement)

    print(f"\nRisk Distribution:")
    risk_dist = scores['risk_flag'].value_counts()
    for flag, count in risk_dist.items():
        pct = count / len(scores) * 100
        print(f"  {flag}: {count:,} ({pct:.1f}%)")

    print(f"\nAvg Engagement Score: {scores['engagement_score'].mean():.1f}")

    # Engagement vs outcomes
    print("\nEngagement vs Outcomes:")
    summary, merged = analyze_engagement_vs_outcomes(scores, enrollment)
    print(summary.to_string(index=False))

    # Charts
    print("\nGenerating charts...")
    plot_engagement_distribution(scores, output_dir)
    plot_engagement_vs_outcome(merged, output_dir)

    # Save scores to warehouse
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')
    conn = sqlite3.connect(db_path)
    scores.to_sql('engagement_scores', conn, if_exists='replace', index=False)
    conn.close()
    print(f"\nScores saved to warehouse ({len(scores):,} rows)")

    print("\nDone.")
