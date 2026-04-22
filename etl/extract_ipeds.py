import pandas as pd

def load_ipeds_file(filepath):
    df = pd.read_csv(filepath, encoding="latin-1")
    print(f"Loaded {filepath} with {len(df)} rows")
    return df

if __name__ == "__main__":
    print("IPEDS loader ready")