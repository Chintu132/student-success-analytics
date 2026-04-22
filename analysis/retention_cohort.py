import pandas as pd

def build_retention_summary(df):
    cohort_df = df.groupby("student_id")["term"].min().reset_index()
    cohort_df.columns = ["student_id", "cohort_term"]

    term_summary = df.groupby("term")["student_id"].nunique().reset_index()
    term_summary.columns = ["term", "student_count"]

    return cohort_df, term_summary

if __name__ == "__main__":
    df = pd.read_csv("data/student_enrollment_sample.csv")

    cohort_df, term_summary = build_retention_summary(df)

    print("Cohort Assignment")
    print(cohort_df)
    print("\nTerm Summary")
    print(term_summary)