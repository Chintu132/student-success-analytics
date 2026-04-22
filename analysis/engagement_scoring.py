import pandas as pd
import numpy as np

def calculate_engagement_score(df):
    df = df.copy()

    df["engagement_score"] = np.where(
        df["credits_earned"] == 0, 20,
        np.where(df["credits_earned"] < df["credits_attempted"], 60, 100)
    )

    return df

if __name__ == "__main__":
    df = pd.read_csv("data/student_enrollment_sample.csv")
    result = calculate_engagement_score(df)

    print("Engagement Scoring")
    print(result[["student_id", "term", "credits_attempted", "credits_earned", "engagement_score"]])