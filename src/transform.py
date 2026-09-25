from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_FILE = Path("data/source/QLFS202602.csv")

# QLFS excludes people under 15 from labour-market questions (they are not
# asked the employment/labour-force questions at all). This matches the
# working-age population definition used by Stats SA / the ILO for QLFS.
WORKING_AGE_MIN = 15

# Columns where Stats SA encodes a "not applicable" skip-pattern answer
# (e.g. an employed person is not asked their reason for unemployment) as
# the literal float value `inf`, rather than as a null. These are valid
# "not applicable" answers, not data-quality problems, so they get
# converted to proper nulls rather than left as `inf` or dropped.
NOT_APPLICABLE_CODE_COLUMNS = [
    "Status",
    "Lfs_Status",
    "Unempl_Status",
    "InactReason",
    "Indus",
    "Occup",
    "PrevIndus",
    "PrevOccup",
    "Sector",
    "Infempl",
    "Long_term_unempl",
    "Underempl",
    "Neet",
    # Hours worked uses the same `inf` "not applicable" encoding for
    # people who are not employed and so were never asked the question.
    "Hrswrk",
]

def remove_unnecessary_columns(df):
    """
    Removes unnecessary columns from the DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    columns_to_remove (list): List of column names to remove.

    Returns:
    pd.DataFrame: DataFrame with unnecessary columns removed.
    """
    columns_to_keep = ["UQNO", "PERSONNO", "SURVEYDATE", "Province", "Metro_code", "Geo_Type_Code", "Stratum", "Q13GENDER", "Q14AGE", "Q16MARITALSTATUS", "Q17EDUCATION", "Q15POPULATION", "Q18FIELD", 
                       "Q19ATTE", "Status", "Lfs_Status", "Unempl_Status", "InactReason", "Indus", "Occup","PrevIndus", "PrevOccup", "Sector", "Infempl", "Long_term_unempl", "Underempl", "Neet",
                       "Graduates", "Education_status", "Age_grp1", "Hrswrk", "Weight"]
    df = df[columns_to_keep]
    
    return df 

def remove_unnecessary_records(df):
    df = df.dropna(subset=["Weight"])
    df = df[df["Weight"] > 0]
        
    return df 

def filter_working_age(df):
    """
    Restrict the dataset to the working-age population (15+), matching the
    population QLFS actually asks labour-market questions of. Household
    members under 15 are out of scope for employment/labour-force analysis
    and, if kept, show up as `inf` in Status/Lfs_Status/Neet etc. because
    those questions were never asked of them.
    """
    df = df[df["Q14AGE"] >= WORKING_AGE_MIN]

    return df

def parse_survey_date(series):
    """
    Parses the raw StatsSA SURVEYDATE field into proper datetimes.

    SURVEYDATE is not a normal date string or serial: it is an unpadded
    integer that concatenates day, month and 4-digit year with no
    separators and no leading zero on the day, e.g. 2052026 means
    day=2, month=05, year=2026 (2 May 2026). Passed straight into
    `pd.to_datetime()`, this integer is instead interpreted as nanoseconds
    since the Unix epoch, which silently produces dates in 1970 for every
    row. Parsing it by digit position (year = last 4 digits, month = the
    2 digits before that, day = whatever remains) avoids that.
    """
    raw = series.astype("Int64").astype(str)

    year = raw.str[-4:]
    month = raw.str[-6:-4]
    day = raw.str[:-6]

    date_str = day + "-" + month + "-" + year

    return pd.to_datetime(date_str, format="%d-%m-%Y", errors="coerce")


def handle_not_applicable_codes(df):
    """
    Converts the `inf` sentinel StatsSA uses for skip-pattern "not
    applicable" answers into proper nulls, in the columns known to use
    that encoding. Left as `inf`, these values silently corrupt any
    downstream aggregation or category dtype conversion.
    """
    for column in NOT_APPLICABLE_CODE_COLUMNS:
        if column in df.columns:
            numeric = pd.to_numeric(df[column], errors="coerce")
            df[column] = numeric.replace([np.inf, -np.inf], np.nan)

    return df

def rename_cols(df):
    """
    Renames columns in the DataFrame to more descriptive names.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: DataFrame with renamed columns.
    """
    df = df.rename(columns={
        "UQNO": "Unique_Questionnaire_Number",
        "PERSONNO": "Person_Number",
        "SURVEYDATE": "Survey_Date",
        "Province": "Province",
        "Metro_code": "Metro_Code",
        "Geo_Type_Code": "Geo_Type_Code",
        "Stratum": "Stratum",
        "Q13GENDER": "Gender",
        "Q14AGE": "Age",
        "Q16MARITALSTATUS": "Marital_Status",
        "Q17EDUCATION": "Education_Level",
        "Q15POPULATION": "Population_Group",
        "Q18FIELD": "Field_of_Study",
        "Q19ATTE": "Attendance_Status",
        "Status": "Employment_Status",
        "Lfs_Status": "Labour_Force_Status",
        "Unempl_Status": "Unemployment_Status",
        "InactReason": "Reason_for_Inactivity",
        "Indus": "Industry_Code",
        "Occup": "Occupation_Code",
        "PrevIndus": "Previous_Industry_Code",
        "PrevOccup": "Previous_Occupation_Code",
        "Sector": "Sector_Code",
        "Infempl": "Informal_Employment_Status",
        "Long_term_unempl": "Long_Term_Unemployment_Status",
        "Underempl": "Underemployment_Status",
        "Neet": "'Not in Education, Employment, or Training' Status",
        'Graduates': 'Graduate Status',
        'Education_status': 'Education Status',
        'Age_grp1': 'Age Group',
        'Hrswrk': 'Hours Worked',
        'Weight': 'Weight'
    })
    
    return df

def convert_data_types(df):

    if "SURVEYDATE" in df.columns:
        df["SURVEYDATE"] = parse_survey_date(df["SURVEYDATE"])

    numeric_columns = [
        "PERSONNO",
        "Metro_code",
        "Geo_Type_Code",
        "Stratum",
        "Q14AGE",
        "Hrswrk",
        "Weight"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df

def change_to_category(df):
    """
    Converts specific columns in the DataFrame to categorical data type.
    """

    categorical_columns = [ "Province", "Q13GENDER", "Q16MARITALSTATUS", "Q17EDUCATION", "Q15POPULATION", "Q18FIELD", "Q19ATTE", "Status", "Lfs_Status", "Unempl_Status", "InactReason", "Indus", "Occup", "PrevIndus", "PrevOccup", "Sector", "Infempl", "Long_term_unempl", "Underempl", "Neet", "Graduates", "Education_status", "Age_grp1" ]

    for column in categorical_columns:
        if column in df.columns: 
            df[column] = df[column].astype("category")
    
    return df

def transform(df):
    """
    Transforms the DataFrame by applying a series of data cleaning and transformation steps.

    Parameters:
    df (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: Transformed DataFrame.
    """
    df = remove_unnecessary_columns(df)
    df = remove_unnecessary_records(df)
    df = filter_working_age(df)
    df = convert_data_types(df)
    df = handle_not_applicable_codes(df)
    df = change_to_category(df)
    df = rename_cols(df)

    # print(df)
    
    return df

# labor_data = pd.read_csv(SOURCE_FILE)
# new_data = transform(labor_data)
# print(new_data["PERSONNO"])

