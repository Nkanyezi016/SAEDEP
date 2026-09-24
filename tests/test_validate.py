import pandas as pd
import pytest

from src.validate import (
    validate_columns,
    validate_nulls,
    validate_data_types,
    validate_age,
    validate_hours_worked,
    validate_survey_date,
    validate_duplicates,
    validate_weight,
    validate,
)


def create_valid_dataframe():
    return pd.DataFrame({
        "Unique_Questionnaire_Number": [1, 2],
        "Person_Number": [1, 1],
        "Survey_Date": pd.to_datetime(
            ["2025-01-01", "2025-01-01"]
        ),
        "Province": ["Gauteng", "Gauteng"],
        "Metro_Code": [1, 1],
        "Geo_Type_Code": [1, 1],
        "Stratum": [1, 1],
        "Gender": ["Male", "Female"],
        "Age": [25, 30],
        "Marital_Status": ["Single", "Married"],
        "Population_Group": ["African", "African"],
        "Education_Level": ["Degree", "Diploma"],
        "Field_of_Study": ["Mathematics", "Education"],
        "Attendance_Status": ["Attending", "Attending"],
        "Employment_Status": ["Employed", "Unemployed"],
        "Labour_Force_Status": ["Labour Force", "Labour Force"],
        "Unemployment_Status": ["Not unemployed", "Unemployed"],
        "Reason_for_Inactivity": [None, None],
        "Industry_Code": [1, 2],
        "Occupation_Code": [1, 2],
        "Previous_Industry_Code": [1, 2],
        "Previous_Occupation_Code": [1, 2],
        "Sector_Code": [1, 1],
        "Informal_Employment_Status": ["No", "No"],
        "Long_Term_Unemployment_Status": ["No", "Yes"],
        "Underemployment_Status": ["No", "No"],
        "'Not in Education, Employment, or Training' Status": [
            "No",
            "No"
        ],
        "Graduate Status": ["Graduate", "Graduate"],
        "Education Status": ["Completed", "Completed"],
        "Age Group": ["25-34", "25-34"],
        "Hours Worked": [40, 0],
        "Weight": [1.5, 2.0],
    })


def test_validate_columns_passes():
    df = create_valid_dataframe()

    assert validate_columns(df) is None


def test_validate_columns_fails_when_column_missing():
    df = create_valid_dataframe()

    df = df.drop(columns=["Gender"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_columns(df)


def test_validate_nulls_passes():
    df = create_valid_dataframe()

    assert validate_nulls(df) is None


def test_validate_nulls_fails():
    df = create_valid_dataframe()

    df.loc[0, "Age"] = None

    with pytest.raises(ValueError, match="Null values"):
        validate_nulls(df)


def test_validate_data_types_passes():
    df = create_valid_dataframe()

    assert validate_data_types(df) is None


def test_validate_data_types_fails():
    df = create_valid_dataframe()

    df["Age"] = ["twenty-five", "thirty"]

    with pytest.raises(ValueError, match="Age must be numeric"):
        validate_data_types(df)


def test_validate_age_passes():
    df = create_valid_dataframe()

    assert validate_age(df) is None


def test_validate_age_fails_for_negative_age():
    df = create_valid_dataframe()

    df.loc[0, "Age"] = -1

    with pytest.raises(ValueError, match="Invalid Age"):
        validate_age(df)


def test_validate_age_fails_for_unrealistic_age():
    df = create_valid_dataframe()

    df.loc[0, "Age"] = 150

    with pytest.raises(ValueError, match="Invalid Age"):
        validate_age(df)


def test_validate_hours_worked_fails_for_negative_value():
    df = create_valid_dataframe()

    df.loc[0, "Hours Worked"] = -5

    with pytest.raises(ValueError, match="Invalid Hours Worked"):
        validate_hours_worked(df)


def test_validate_survey_date_fails_for_invalid_date():
    df = create_valid_dataframe()

    df["Survey_Date"] = ["not-a-date", "2025-01-01"]

    with pytest.raises(ValueError, match="Invalid Survey_Date"):
        validate_survey_date(df)


def test_validate_duplicates_fails():
    df = create_valid_dataframe()

    # Make both records represent the same respondent
    df.loc[1, "Unique_Questionnaire_Number"] = 1
    df.loc[1, "Person_Number"] = 1

    with pytest.raises(
        ValueError,
        match="Duplicate respondent records"
    ):
        validate_duplicates(df)


def test_validate_weight_fails_for_negative_weight():
    df = create_valid_dataframe()

    df.loc[0, "Weight"] = -1

    with pytest.raises(ValueError, match="Invalid Weight"):
        validate_weight(df)


def test_complete_validation_passes():
    df = create_valid_dataframe()

    assert validate(df) is True