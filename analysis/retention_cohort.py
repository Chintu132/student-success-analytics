import pandas as pd

def build_retention_summary(df, student_col, term_col):
    first_term = df.groupby(student_col)[term_col].min().reset_index()
    first_term.columns = [student_col, "cohort_term"]
    return first_term

if __name__ == "__main__":
    print("Retention analysis script ready")