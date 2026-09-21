### This file is for getting the original data from its source, verify that it is correct, and then store it in a local file for later use.
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
SOURCE_FILE = Path("data/source/QLFS202602.csv")
OUTPUT_FILE = RAW_DIR / "QLFS202602.csv"

def ingest_qlfs():
    RAW_DIR.mkdir(parents=True, exist_ok=True) # Create the raw data directory if it doesn't exist
    
    if not SOURCE_FILE.exists():
        raise FileNotFoundError(f"QLFS file does not exist: {SOURCE_FILE}")
    
    labor_data = pd.read_csv(SOURCE_FILE)
    
    if labor_data.empty:
        raise ValueError("The QLFS data is empty.")
    
    print(f"Rows: {len(labor_data)}")
    print(f"Columns: {len(labor_data.columns)}")
    
    labor_data.to_csv(OUTPUT_FILE, index=False)
    
    print(f"QLFS data ingested and saved to {OUTPUT_FILE}")
    

if __name__ == "__main__":
    ingest_qlfs()

#labor_data = pd.read_csv(SOURCE_FILE)
# print(labor_data.columns)
