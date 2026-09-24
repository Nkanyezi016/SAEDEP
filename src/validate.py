"""
This checks if the transformed data is clean, structurally correct and safe to load.
"""

import pandas as pd


REQUIRED_COLUMNS = [
    "Unique_Questionnaire_Number",
    "Person_Number",
    "Survey_Date",
    "Province",
    "Metro_Code",
    "Geo_Type_Code",
    "Stratum",
    "Gender",
    "Age",
    "Marital_Status",
    "Population_Group",
    "Education_Level",
    "Field_of_Study",
    "Attendance_Status",
    "Employment_Status",
    "Labour_Force_Status",
    "Unemployment_Status",
    "Reason_for_Inactivity",
    "Industry_Code",
    "Occupation_Code",
    "Previous_Industry_Code",
    "Previous_Occupation_Code",
    "Sector_Code",
    "Informal_Employment_Status",
    "Long_Term_Unemployment_Status",
    "Underemployment_Status",
    "'Not in Education, Employment, or Training' Status",
    "Graduate Status",
    "Education Status",
    "Age Group",
    "Hours Worked",
    "Weight"
]

CRITICAL_COLUMNS = [
    "Unique_Questionnaire_Number",
    "Person_Number",
    "Survey_Date",
    "Age",
    "Gender",
    "Employment_Status",
    "Labour_Force_Status"
]

def validate_columns(df):
    """
    Check that all expected transformed columns are present.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

def validate_nulls(df):
    """
    Check for null values in critical columns.
    """

    null_counts = df[CRITICAL_COLUMNS].isnull().sum()

    null_counts = null_counts[null_counts > 0]

    if not null_counts.empty:
        raise ValueError(
            f"Null values found in critical columns:\n"
            f"{null_counts}"
        )

def validate_data_types(df):
    """
    Validate the data types of important columns.
    """

    if not pd.api.types.is_numeric_dtype(
        df["Age"]
    ):
        raise ValueError(
            "Age must be numeric."
        )

    if not pd.api.types.is_numeric_dtype(
        df["Hours Worked"]
    ):
        raise ValueError(
            "Hours Worked must be numeric."
        )

    if not pd.api.types.is_numeric_dtype(
        df["Weight"]
    ):
        raise ValueError(
            "Weight must be numeric."
        )

def validate_age(df):
    """
    Check that age values are within a reasonable range.
    """

    invalid_age = df[
        (df["Age"] < 0) |
        (df["Age"] > 120)
    ]

    if not invalid_age.empty:
        raise ValueError(
            f"Invalid Age values found: "
            f"{len(invalid_age)} records."
        )

def validate_hours_worked(df):
    """
    Check that hours worked are not negative.
    """

    invalid_hours = df[
        df["Hours Worked"] < 0
    ]

    if not invalid_hours.empty:
        raise ValueError(
            f"Invalid Hours Worked values found: "
            f"{len(invalid_hours)} records."
        )

def validate_survey_date(df):
    """
    Check that Survey_Date contains valid dates.
    """

    invalid_dates = pd.to_datetime(
        df["Survey_Date"],
        errors="coerce"
    ).isna()

    if invalid_dates.any():
        raise ValueError(
            f"Invalid Survey_Date values found: "
            f"{invalid_dates.sum()} records."
        )

def validate_duplicates(df):
    """
    Check for duplicate questionnaire/person combinations.

    A person is identified using both the questionnaire number
    and the person number.
    """

    duplicates = df.duplicated(
        subset=[
            "Unique_Questionnaire_Number",
            "Person_Number"
        ],
        keep=False
    )

    if duplicates.any():
        raise ValueError(
            f"Duplicate respondent records found: "
            f"{duplicates.sum()} records."
        )

def validate_weight(df):
    """
    Check that survey weights are not negative.
    """

    invalid_weights = df[
        df["Weight"] < 0
    ]

    if not invalid_weights.empty:
        raise ValueError(
            f"Invalid Weight values found: "
            f"{len(invalid_weights)} records."
        )

def validate(df):
    """
    Run all validation checks on the transformed QLFS data.
    """

    validate_columns(df)
    validate_nulls(df)
    validate_data_types(df)
    validate_age(df)
    validate_hours_worked(df)
    validate_survey_date(df)
    validate_duplicates(df)
    validate_weight(df)

    print("Data validation passed successfully.")

    return True