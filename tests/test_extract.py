import pandas as pd

from src.extract import extract_data


def test_extract_returns_dataframe(tmp_path):

    input_file = tmp_path / "qlfs.csv"

    test_data = pd.DataFrame({
        "UQNO": [1, 2],
        "PERSONNO": [1, 1],
        "Q14AGE": [25, 30],
    })

    test_data.to_csv(input_file, index=False)

    result = extract_data(input_file)

    assert isinstance(result, pd.DataFrame)


def test_extract_returns_correct_number_of_records(tmp_path):

    input_file = tmp_path / "qlfs.csv"

    test_data = pd.DataFrame({
        "UQNO": [1, 2, 3],
        "PERSONNO": [1, 1, 1],
        "Q14AGE": [25, 30, 35],
    })

    test_data.to_csv(input_file, index=False)

    result = extract_data(input_file)

    assert len(result) == 3