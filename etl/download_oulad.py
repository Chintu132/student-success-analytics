"""
Download the Open University Learning Analytics Dataset (OULAD).
If download fails (no network), generates synthetic data that mirrors OULAD structure.

OULAD source: https://analyse.kmi.open.ac.uk/open_dataset
"""
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'oulad')
OULAD_URL = "https://analyse.kmi.open.ac.uk/open_dataset/download"


def download_oulad():
    """Attempt to download OULAD dataset."""
    try:
        import requests, zipfile, io
        print("Downloading OULAD dataset...")
        resp = requests.get(OULAD_URL, timeout=30)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            z.extractall(DATA_DIR)
        print(f"OULAD downloaded and extracted to {DATA_DIR}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def generate_synthetic_oulad():
    """
    Generate synthetic data that mirrors OULAD's schema exactly.
    Tables: studentInfo, courses, studentRegistration, studentAssessment,
            assessments, studentVle, vle
    """
    import pandas as pd
    import numpy as np

    np.random.seed(42)
    os.makedirs(DATA_DIR, exist_ok=True)

    # --- Courses ---
    modules = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF', 'GGG']
    presentations = ['2013B', '2013J', '2014B', '2014J']
    courses_rows = []
    for mod in modules:
        for pres in presentations:
            courses_rows.append({
                'code_module': mod,
                'code_presentation': pres,
                'module_presentation_length': np.random.choice([234, 241, 262, 269])
            })
    courses = pd.DataFrame(courses_rows)
    courses.to_csv(os.path.join(DATA_DIR, 'courses.csv'), index=False)
    print(f"  courses: {len(courses)} rows")

    # --- Students (studentInfo) ---
    n_students = 32000
    student_ids = list(range(10000, 10000 + n_students))

    regions = ['East Anglian Region', 'Scotland', 'South East Region',
               'West Midlands Region', 'South West Region', 'Wales',
               'North Western Region', 'Yorkshire Region', 'London Region',
               'East Midlands Region', 'North Region', 'Ireland']
    educations = ['No Formal quals', 'Lower Than A Level', 'A Level or Equivalent',
                  'HE Qualification', 'Post Graduate Qualification']
    imd_bands = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%',
                 '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
    age_bands = ['0-35', '35-55', '55<=']
    final_results = ['Pass', 'Fail', 'Withdrawn', 'Distinction']

    student_rows = []
    for sid in student_ids:
        mod = np.random.choice(modules)
        pres = np.random.choice(presentations)
        n_prev = np.random.choice([0, 0, 0, 0, 1, 1, 2], p=[0.55, 0.15, 0.1, 0.05, 0.07, 0.05, 0.03])
        credits = np.random.choice([30, 60, 90, 120, 150, 240])

        # Simulate realistic outcome distribution
        result = np.random.choice(
            final_results,
            p=[0.38, 0.15, 0.32, 0.15]
        )

        student_rows.append({
            'code_module': mod,
            'code_presentation': pres,
            'id_student': sid,
            'gender': np.random.choice(['M', 'F']),
            'region': np.random.choice(regions),
            'highest_education': np.random.choice(educations, p=[0.05, 0.35, 0.35, 0.15, 0.10]),
            'imd_band': np.random.choice(imd_bands),
            'age_band': np.random.choice(age_bands, p=[0.72, 0.24, 0.04]),
            'num_of_prev_attempts': n_prev,
            'studied_credits': credits,
            'disability': np.random.choice(['Y', 'N'], p=[0.10, 0.90]),
            'final_result': result,
            'date_registration': np.random.randint(-200, 0),
            'date_unregistration': '' if result in ['Pass', 'Distinction'] else np.random.randint(50, 260),
        })

    student_info = pd.DataFrame(student_rows)
    student_info.to_csv(os.path.join(DATA_DIR, 'studentInfo.csv'), index=False)
    print(f"  studentInfo: {len(student_info)} rows")

    # --- Student Registration ---
    reg_rows = []
    for _, row in student_info.iterrows():
        reg_rows.append({
            'code_module': row['code_module'],
            'code_presentation': row['code_presentation'],
            'id_student': row['id_student'],
            'date_registration': row['date_registration'],
            'date_unregistration': row['date_unregistration'],
        })
    student_reg = pd.DataFrame(reg_rows)
    student_reg.to_csv(os.path.join(DATA_DIR, 'studentRegistration.csv'), index=False)
    print(f"  studentRegistration: {len(student_reg)} rows")

    # --- Assessments ---
    assessment_types = ['TMA', 'CMA', 'Exam']
    assess_rows = []
    assess_id = 1000
    for mod in modules:
        for pres in presentations:
            n_assessments = np.random.randint(4, 8)
            for i in range(n_assessments):
                atype = 'Exam' if i == n_assessments - 1 else np.random.choice(['TMA', 'CMA'])
                assess_rows.append({
                    'code_module': mod,
                    'code_presentation': pres,
                    'id_assessment': assess_id,
                    'assessment_type': atype,
                    'date': np.random.randint(20, 260) if atype != 'Exam' else '',
                    'weight': 10 if atype != 'Exam' else 50,
                })
                assess_id += 1
    assessments = pd.DataFrame(assess_rows)
    assessments.to_csv(os.path.join(DATA_DIR, 'assessments.csv'), index=False)
    print(f"  assessments: {len(assessments)} rows")

    # --- Student Assessments ---
    sa_rows = []
    for _, student in student_info.iterrows():
        mod_assessments = assessments[
            (assessments['code_module'] == student['code_module']) &
            (assessments['code_presentation'] == student['code_presentation'])
        ]
        for _, assess in mod_assessments.iterrows():
            # Skip some assessments for withdrawn/failed students
            if student['final_result'] == 'Withdrawn' and np.random.random() > 0.5:
                continue
            if student['final_result'] == 'Fail' and np.random.random() > 0.8:
                continue

            if student['final_result'] == 'Distinction':
                score = np.random.randint(70, 100)
            elif student['final_result'] == 'Pass':
                score = np.random.randint(45, 85)
            elif student['final_result'] == 'Fail':
                score = np.random.randint(10, 50)
            else:
                score = np.random.randint(20, 60)

            sa_rows.append({
                'id_assessment': assess['id_assessment'],
                'id_student': student['id_student'],
                'date_submitted': np.random.randint(1, 260),
                'is_banked': 0,
                'score': score,
            })

    student_assess = pd.DataFrame(sa_rows)
    student_assess.to_csv(os.path.join(DATA_DIR, 'studentAssessment.csv'), index=False)
    print(f"  studentAssessment: {len(student_assess)} rows")

    # --- VLE (Virtual Learning Environment) sites ---
    activity_types = ['forumng', 'oucontent', 'resource', 'subpage', 'homepage',
                       'quiz', 'url', 'ouwiki', 'glossary', 'questionnaire',
                       'page', 'ouelluminate', 'oucollaborate', 'dataplus']
    vle_rows = []
    site_id = 5000
    for mod in modules:
        for pres in presentations:
            n_sites = np.random.randint(30, 80)
            for _ in range(n_sites):
                vle_rows.append({
                    'id_site': site_id,
                    'code_module': mod,
                    'code_presentation': pres,
                    'activity_type': np.random.choice(activity_types),
                    'week_from': np.random.randint(1, 20),
                    'week_to': np.random.randint(20, 40),
                })
                site_id += 1
    vle = pd.DataFrame(vle_rows)
    vle.to_csv(os.path.join(DATA_DIR, 'vle.csv'), index=False)
    print(f"  vle: {len(vle)} rows")

    # --- Student VLE (clickstream) ---
    # This is the biggest table — generate realistic clickstream data
    print("  Generating studentVle clickstream data (this takes a moment)...")
    svle_rows = []
    sample_students = student_info.sample(min(8000, len(student_info)), random_state=42)

    for _, student in sample_students.iterrows():
        mod_sites = vle[
            (vle['code_module'] == student['code_module']) &
            (vle['code_presentation'] == student['code_presentation'])
        ]['id_site'].values

        if len(mod_sites) == 0:
            continue

        # Engaged students have more activity days
        if student['final_result'] in ['Pass', 'Distinction']:
            n_days = np.random.randint(30, 180)
        elif student['final_result'] == 'Fail':
            n_days = np.random.randint(10, 80)
        else:  # Withdrawn
            n_days = np.random.randint(5, 50)

        for day in sorted(np.random.choice(range(-20, 260), size=min(n_days, 200), replace=False)):
            n_sites_visited = np.random.randint(1, 6)
            for site in np.random.choice(mod_sites, size=min(n_sites_visited, len(mod_sites)), replace=False):
                svle_rows.append({
                    'code_module': student['code_module'],
                    'code_presentation': student['code_presentation'],
                    'id_student': student['id_student'],
                    'id_site': site,
                    'date': int(day),
                    'sum_click': np.random.randint(1, 20),
                })

    student_vle = pd.DataFrame(svle_rows)
    student_vle.to_csv(os.path.join(DATA_DIR, 'studentVle.csv'), index=False)
    print(f"  studentVle: {len(student_vle)} rows")

    print(f"\nSynthetic OULAD data generated in {DATA_DIR}")
    return True


if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)

    # Check if data already exists
    if os.path.exists(os.path.join(DATA_DIR, 'studentInfo.csv')):
        print("OULAD data already exists. Delete data/oulad/ to regenerate.")
        sys.exit(0)

    # Try download first, fall back to synthetic
    if not download_oulad():
        print("\nGenerating synthetic OULAD data instead...")
        generate_synthetic_oulad()
