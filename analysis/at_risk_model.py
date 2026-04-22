import pandas as pd
import numpy as np

def flag_at_risk_students(df):
    df = df.copy()

    df["at_risk_flag"] = np.where(
        (df["final_grade"].isin(["W", "F"])) | (df["credits_earned"] == 0),
        "Yes",
        "No"
    )

    return df

if __name__ == "__main__":
    df = pd.read_csv("data/student_enrollment_sample.csv")
    result = flag_at_risk_students(df)

    print("At-Risk Student Flag")
    print(result[["student_id", "term", "final_grade", "credits_earned", "at_risk_flag"]])