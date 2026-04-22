import pandas as pd
from pathlib import Path

def load_oulad_tables(data_dir="data/oulad"):
    tables = {}
    for file_path in Path(data_dir).glob("*.csv"):
        tables[file_path.stem] = pd.read_csv(file_path)
        print(f"Loaded {file_path.stem}: {len(tables[file_path.stem])} rows")
    return tables

if __name__ == "__main__":
    load_oulad_tables()