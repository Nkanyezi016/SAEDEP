import pandas as pd
from pathlib import Path

def load_data(df, output_path):
    """
    Load validated QLFS data into a processed CSV file.

    Parameters:
    df (pd.DataFrame): The DataFrame to be saved.
    output_path (str): The path where the CSV file will be saved.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories if they don't exist

    df.to_csv(output_path, index=False)

    print(f"Data successfully loaded to {output_path}")

