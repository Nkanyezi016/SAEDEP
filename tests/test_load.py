import pandas as pd

from src.load import load_data


def test_load_creates_csv(tmp_path):

    df = pd.DataFrame({
        "Person_Number": [1, 2],
        "Age": [25, 30],
        "Gender": ["Male", "Female"],
    })

    output_file = tmp_path / "qlfs_processed.csv"

    load_data(df, output_file)

    assert output_file.exists()


def test_loaded_data_matches_original(tmp_path):

    df = pd.DataFrame({
        "Person_Number": [1, 2],
        "Age": [25, 30],
        "Gender": ["Male", "Female"],
    })

    output_file = tmp_path / "qlfs_processed.csv"

    load_data(df, output_file)

    loaded_df = pd.read_csv(output_file)

    pd.testing.assert_frame_equal(
        df,
        loaded_df
    )