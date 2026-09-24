### This file is for getting the original data from its source,
### verifying that it is correct, and storing it locally for later use.

from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")
SOURCE_FILE = Path("data/source/QLFS202602.csv")
OUTPUT_FILE = RAW_DIR / "QLFS202602.csv"


def extract_data(input_file):
    """
    Extract QLFS data from a CSV file and return it as a DataFrame.
    """

    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"QLFS file does not exist: {input_file}")

    labor_data = pd.read_csv(input_file)

    if labor_data.empty:
        raise ValueError("The QLFS data is empty.")

    return labor_data


def ingest_qlfs():
    """
    Extract the QLFS source data and save a copy to the raw data directory.
    """

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    labor_data = extract_data(SOURCE_FILE)

    print(f"Rows: {len(labor_data)}")
    print(f"Columns: {len(labor_data.columns)}")

    labor_data.to_csv(OUTPUT_FILE, index=False)

    print(f"QLFS data ingested and saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    ingest_qlfs()