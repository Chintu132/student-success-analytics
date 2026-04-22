import pandas as pd
from sklearn.linear_model import LogisticRegression

def build_model():
    model = LogisticRegression()
    return model

if __name__ == "__main__":
    print("At-risk model script ready")