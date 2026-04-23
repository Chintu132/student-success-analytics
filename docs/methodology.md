# Methodology — How Metrics Are Calculated

## 1. Retention Rate

**Definition:** The percentage of a starting cohort that returns for each subsequent term.

**Calculation:**
```
Retention Rate (Term N) = Students enrolled in Term N from cohort / Cohort size × 100
```

**Cohort definition:** A student's cohort is defined by their first term of enrollment. Students appearing in multiple modules within the same term are counted once.

**Standard:** This follows IPEDS methodology for first-time, full-time retention rates as reported to SACSCOC and the U.S. Department of Education.

## 2. DFW Rate

**Definition:** The percentage of students in a course who earn a D, F, or Withdraw.

**Calculation:**
```
DFW Rate = (D grades + F grades + Withdrawals) / Total Enrolled × 100
```

**OULAD mapping:** Since OULAD uses Pass/Distinction/Fail/Withdrawn rather than letter grades, we map Fail and Withdrawn as DFW outcomes.

**Barrier course threshold:** Courses with DFW rates above 40% are flagged as barrier courses, following common IR practice.

## 3. Engagement Score

**Definition:** A composite score (0–100) measuring a student's LMS/VLE activity level relative to their peers in the same course.

**Components:**
- Click volume percentile (40% weight) — total VLE interactions ranked within course
- Activity consistency (40% weight) — percentage of available weeks with at least one interaction
- Site diversity percentile (20% weight) — breadth of VLE resources accessed

**Risk thresholds:**
- Below 40 = AT-RISK (recommend intervention)
- 40–60 = WATCH (monitor closely)
- Above 60 = ON-TRACK

## 4. At-Risk Prediction Model

**Type:** Logistic Regression (binary classification)

**Target:** Pass/Distinction (1) vs Fail/Withdrawn (0)

**Features:**
- gender_encoded (binary)
- disability_encoded (binary)
- age_encoded (ordinal: 0-35=0, 35-55=1, 55<=2)
- education_encoded (ordinal: No Formal=0 through Post Graduate=4)
- prev_attempts (count, capped at 3)
- studied_credits (continuous)
- engagement_score (continuous, 0-100)

**Evaluation:** AUC-ROC, classification report (precision/recall/F1), confusion matrix

**Why logistic regression?** IR offices need interpretable models that can be explained to provosts and accreditors. Coefficients map directly to "this factor increases/decreases pass probability by X." Black-box models are harder to act on.
