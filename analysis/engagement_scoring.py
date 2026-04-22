import pandas as pd
import numpy as np

def calculate_engagement_score(df, activity_col):
    df = df.copy()
    df["engagement_score"] = np.where(df[activity_col] > 0, 100, 0)
    return df

if __name__ == "__main__":
    print("Engagement scoring script ready")