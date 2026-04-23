"""
Cohort Retention Analysis
=========================
Tracks what % of a starting cohort returns each subsequent term.
This is THE analysis every IR office runs and reports to accreditors.

Output: retention curve chart + cohort summary table.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlite3


def load_enrollment_data():
    """Load enrollment data from warehouse."""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM fact_enrollment", conn)
    conn.close()
    return df


def build_retention_cohort(enrollment_df):
    """
    Build cohort retention table.

    For each cohort (defined by first term), calculate what % of students
    appeared in each subsequent term.
    """
    # Identify each student's first term (cohort)
    first_term = (enrollment_df
        .groupby('id_student')['code_presentation']
        .min()
        .reset_index()
        .rename(columns={'code_presentation': 'cohort_term'})
    )

    # Get all terms
    all_terms = sorted(enrollment_df['code_presentation'].unique())

    results = []
    for cohort_term in all_terms:
        cohort_students = first_term[first_term['cohort_term'] == cohort_term]['id_student']
        cohort_size = len(cohort_students)
        if cohort_size < 10:
            continue

        cohort_data = enrollment_df[enrollment_df['id_student'].isin(cohort_students)]

        for i, term in enumerate(all_terms):
            if term < cohort_term:
                continue
            enrolled = cohort_data[cohort_data['code_presentation'] == term]['id_student'].nunique()
            results.append({
                'cohort_term': cohort_term,
                'term': term,
                'term_number': all_terms.index(term) - all_terms.index(cohort_term) + 1,
                'cohort_size': cohort_size,
                'enrolled': enrolled,
                'retention_rate': round(enrolled / cohort_size * 100, 1)
            })

    return pd.DataFrame(results)


def build_outcome_summary(enrollment_df):
    """Summary of outcomes by cohort term."""
    first_term = (enrollment_df
        .groupby('id_student')['code_presentation']
        .min()
        .reset_index()
        .rename(columns={'code_presentation': 'cohort_term'})
    )

    # Get latest result per student
    latest = (enrollment_df
        .sort_values('code_presentation')
        .drop_duplicates(subset=['id_student'], keep='last')
        [['id_student', 'final_result']]
    )

    merged = first_term.merge(latest, on='id_student')
    summary = (merged
        .groupby(['cohort_term', 'final_result'])
        .size()
        .reset_index(name='count')
    )

    # Pivot for readability
    pivot = summary.pivot_table(
        index='cohort_term', columns='final_result',
        values='count', fill_value=0
    )
    pivot['total'] = pivot.sum(axis=1)

    for col in ['Pass', 'Distinction', 'Fail', 'Withdrawn']:
        if col in pivot.columns:
            pivot[f'{col}_pct'] = (pivot[col] / pivot['total'] * 100).round(1)

    return pivot


def plot_retention_curves(retention_df, output_dir):
    """Plot retention curves — one line per cohort."""
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ['#003366', '#0066CC', '#CC3333', '#339933']
    cohorts = sorted(retention_df['cohort_term'].unique())

    for i, cohort in enumerate(cohorts):
        data = retention_df[retention_df['cohort_term'] == cohort]
        color = colors[i % len(colors)]
        ax.plot(data['term_number'], data['retention_rate'],
                marker='o', linewidth=2, color=color,
                label=f'Cohort {cohort} (n={data["cohort_size"].iloc[0]:,})')

    ax.set_xlabel('Term Number', fontsize=12)
    ax.set_ylabel('Retention Rate (%)', fontsize=12)
    ax.set_title('Cohort Retention Curves', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 105)
    ax.axhline(y=60, color='red', linestyle='--', alpha=0.4, label='60% Benchmark')
    ax.legend(loc='lower left', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'retention_curves.png')
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"  Chart saved: {filepath}")


def plot_outcome_distribution(enrollment_df, output_dir):
    """Stacked bar chart of outcomes by cohort."""
    fig, ax = plt.subplots(figsize=(10, 6))

    first_term = (enrollment_df
        .groupby('id_student')['code_presentation']
        .min()
        .reset_index()
        .rename(columns={'code_presentation': 'cohort_term'})
    )
    latest = (enrollment_df
        .sort_values('code_presentation')
        .drop_duplicates(subset=['id_student'], keep='last')
        [['id_student', 'final_result']]
    )
    merged = first_term.merge(latest, on='id_student')

    ct = pd.crosstab(merged['cohort_term'], merged['final_result'], normalize='index') * 100

    color_map = {
        'Distinction': '#1a9641',
        'Pass': '#a6d96a',
        'Fail': '#fdae61',
        'Withdrawn': '#d7191c'
    }
    order = [c for c in ['Distinction', 'Pass', 'Fail', 'Withdrawn'] if c in ct.columns]
    ct[order].plot(kind='bar', stacked=True, ax=ax,
                   color=[color_map.get(c, '#999') for c in order])

    ax.set_ylabel('Percentage (%)', fontsize=12)
    ax.set_xlabel('Cohort Term', fontsize=12)
    ax.set_title('Student Outcome Distribution by Cohort', fontsize=14, fontweight='bold')
    ax.legend(title='Outcome', bbox_to_anchor=(1.02, 1), loc='upper left')
    ax.set_ylim(0, 100)
    plt.xticks(rotation=0)
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'outcome_distribution.png')
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"  Chart saved: {filepath}")


if __name__ == '__main__':
    print("=" * 60)
    print("RETENTION COHORT ANALYSIS")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'dashboards', 'screenshots')
    os.makedirs(output_dir, exist_ok=True)

    enrollment = load_enrollment_data()
    print(f"\nLoaded {len(enrollment):,} enrollment records")

    # Build cohort retention
    print("\nBuilding cohort retention table...")
    retention = build_retention_cohort(enrollment)
    print(retention.to_string(index=False))

    # Outcome summary
    print("\nOutcome Summary by Cohort:")
    summary = build_outcome_summary(enrollment)
    print(summary.to_string())

    # Charts
    print("\nGenerating charts...")
    plot_retention_curves(retention, output_dir)
    plot_outcome_distribution(enrollment, output_dir)

    print("\nDone.")
