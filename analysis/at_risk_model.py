"""
At-Risk Student Prediction Model
=================================
Logistic regression combining demographics + engagement score to predict pass/fail.
Not deep ML — practical, interpretable, the kind of model IR offices actually use.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, roc_curve, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import sqlite3
import json


def load_data():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'warehouse.db')
    conn = sqlite3.connect(db_path)
    students = pd.read_sql("SELECT * FROM dim_student", conn)
    enrollment = pd.read_sql("SELECT * FROM fact_enrollment", conn)

    # Check if engagement scores exist
    try:
        scores = pd.read_sql("SELECT * FROM engagement_scores", conn)
    except Exception:
        scores = None
        print("  NOTE: Run engagement_scoring.py first for best results")

    conn.close()
    return students, enrollment, scores


def build_features(students, enrollment, scores):
    """
    Build feature matrix for prediction.
    Features: demographics + engagement score.
    Target: passed (1) vs failed/withdrawn (0).
    """
    # Start with enrollment data — drop duplicate columns before merge
    students_clean = students.drop(columns=['studied_credits'], errors='ignore')
    df = enrollment.merge(students_clean, on='id_student', how='left')

    # Encode categoricals
    df['gender_encoded'] = (df['gender'] == 'M').astype(int)
    df['disability_encoded'] = (df['disability'] == 'Yes').astype(int)

    age_map = {'0-35': 0, '35-55': 1, '55<=': 2, 'Unknown': 0}
    df['age_encoded'] = df['age_band'].map(age_map).fillna(0).astype(int)

    edu_map = {
        'No Formal quals': 0, 'Lower Than A Level': 1,
        'A Level or Equivalent': 2, 'HE Qualification': 3,
        'Post Graduate Qualification': 4, 'Unknown': 1
    }
    df['education_encoded'] = df['highest_education'].map(edu_map).fillna(1).astype(int)
    df['prev_attempts'] = df['num_of_prev_attempts'].clip(0, 3)

    # Add engagement score if available
    if scores is not None:
        df = df.merge(
            scores[['id_student', 'code_module', 'code_presentation', 'engagement_score']],
            on=['id_student', 'code_module', 'code_presentation'],
            how='left'
        )
        df['engagement_score'] = df['engagement_score'].fillna(df['engagement_score'].median())
    else:
        df['engagement_score'] = 50  # neutral default

    # Target: passed (includes Distinction)
    df['target'] = df['passed'].astype(int)

    feature_cols = ['gender_encoded', 'disability_encoded', 'age_encoded',
                    'education_encoded', 'prev_attempts', 'studied_credits',
                    'engagement_score']

    X = df[feature_cols].copy()
    y = df['target'].copy()

    # Drop rows with any NaN
    valid_mask = X.notna().all(axis=1) & y.notna()
    X = X[valid_mask]
    y = y[valid_mask]

    return X, y, feature_cols


def train_model(X, y, feature_cols):
    """Train logistic regression and report results."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Fail/Withdraw', 'Pass/Distinction']))

    auc = roc_auc_score(y_test, y_proba)
    print(f"AUC-ROC: {auc:.3f}")

    # Feature importance
    print("\nFeature Importance (coefficients):")
    for name, coef in sorted(zip(feature_cols, model.coef_[0]),
                              key=lambda x: abs(x[1]), reverse=True):
        direction = "↑ helps pass" if coef > 0 else "↓ hurts pass"
        print(f"  {name}: {coef:+.3f} ({direction})")

    return model, X_test, y_test, y_proba, auc


def plot_roc_curve(y_test, y_proba, auc, output_dir):
    """Plot ROC curve."""
    fig, ax = plt.subplots(figsize=(8, 6))
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    ax.plot(fpr, tpr, color='#003366', linewidth=2, label=f'Model (AUC = {auc:.3f})')
    ax.plot([0, 1], [0, 1], color='gray', linestyle='--', alpha=0.5, label='Random (AUC = 0.500)')
    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('At-Risk Prediction — ROC Curve', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'roc_curve.png')
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"  Chart saved: {filepath}")


def plot_feature_importance(model, feature_cols, output_dir):
    """Horizontal bar chart of feature coefficients."""
    fig, ax = plt.subplots(figsize=(8, 5))

    coefs = pd.Series(model.coef_[0], index=feature_cols).sort_values()
    colors = ['#d7191c' if c < 0 else '#1a9641' for c in coefs]
    coefs.plot(kind='barh', ax=ax, color=colors)

    ax.set_xlabel('Coefficient (+ = helps pass, - = hurts pass)', fontsize=11)
    ax.set_title('Feature Importance — At-Risk Model', fontsize=14, fontweight='bold')
    ax.axvline(x=0, color='black', linewidth=0.5)
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()

    filepath = os.path.join(output_dir, 'feature_importance.png')
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"  Chart saved: {filepath}")


def plot_confusion_matrix(y_test, y_pred, output_dir):
    """Plot confusion matrix."""
    fig, ax = plt.subplots(figsize=(6, 5))
    cm = confusion_matrix(y_test, y_pred)
    im = ax.imshow(cm, cmap='Blues')

    labels = ['Fail/Withdraw', 'Pass/Distinction']
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel('Predicted', fontsize=12)
    ax.set_ylabel('Actual', fontsize=12)
    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')

    for i in range(2):
        for j in range(2):
            ax.text(j, i, f'{cm[i, j]:,}', ha='center', va='center', fontsize=14,
                    color='white' if cm[i, j] > cm.max() / 2 else 'black')

    plt.tight_layout()
    filepath = os.path.join(output_dir, 'confusion_matrix.png')
    plt.savefig(filepath, dpi=150)
    plt.close()
    print(f"  Chart saved: {filepath}")


if __name__ == '__main__':
    print("=" * 60)
    print("AT-RISK STUDENT PREDICTION MODEL")
    print("=" * 60)

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'dashboards', 'screenshots')
    os.makedirs(output_dir, exist_ok=True)

    students, enrollment, scores = load_data()
    print(f"\nStudents: {len(students):,}, Enrollments: {len(enrollment):,}")

    # Build features
    print("\nBuilding feature matrix...")
    X, y, feature_cols = build_features(students, enrollment, scores)
    print(f"Feature matrix: {X.shape[0]:,} rows, {X.shape[1]} features")
    print(f"Target distribution: {y.value_counts().to_dict()}")

    # Train model
    print("\nTraining logistic regression...")
    model, X_test, y_test, y_proba, auc = train_model(X, y, feature_cols)
    y_pred = model.predict(X_test)

    # Charts
    print("\nGenerating charts...")
    plot_roc_curve(y_test, y_proba, auc, output_dir)
    plot_feature_importance(model, feature_cols, output_dir)
    plot_confusion_matrix(y_test, y_pred, output_dir)

    # Save model metrics
    metrics = {
        'auc_roc': round(auc, 3),
        'features': feature_cols,
        'coefficients': {name: round(float(coef), 3)
                         for name, coef in zip(feature_cols, model.coef_[0])},
        'training_samples': int(X.shape[0] * 0.8),
        'test_samples': int(X.shape[0] * 0.2),
    }
    metrics_path = os.path.join(os.path.dirname(__file__), '..', 'docs', 'model_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"\nModel metrics saved to {metrics_path}")

    print("\nDone.")
