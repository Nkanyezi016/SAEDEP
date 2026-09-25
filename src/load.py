import pandas as pd
from pathlib import Path

from src.db import get_engine, load_dataframe, run_sql_dir

SCHEMA = "staging"
TABLE = "qlfs_responses"

# The transform stage produces business-friendly display names for use in
# CSV output (some with spaces and punctuation, e.g. "Hours Worked").
# Those aren't valid unquoted SQL identifiers, so the Postgres load uses
# these clean, stable, snake_case names instead. This mapping is the
# single source of truth for how a pandas column maps to a SQL column.
SQL_COLUMN_MAP = {
    "Unique_Questionnaire_Number": "unique_questionnaire_number",
    "Person_Number": "person_number",
    "Survey_Date": "survey_date",
    "Province": "province_code",
    "Metro_Code": "metro_code",
    "Geo_Type_Code": "geo_type_code",
    "Stratum": "stratum",
    "Gender": "gender_code",
    "Age": "age",
    "Marital_Status": "marital_status_code",
    "Population_Group": "population_group_code",
    "Education_Level": "education_level_code",
    "Field_of_Study": "field_of_study_code",
    "Attendance_Status": "attendance_status_code",
    "Employment_Status": "employment_status_code",
    "Labour_Force_Status": "labour_force_status_code",
    "Unemployment_Status": "unemployment_status_code",
    "Reason_for_Inactivity": "reason_for_inactivity_code",
    "Industry_Code": "industry_code",
    "Occupation_Code": "occupation_code",
    "Previous_Industry_Code": "previous_industry_code",
    "Previous_Occupation_Code": "previous_occupation_code",
    "Sector_Code": "sector_code",
    "Informal_Employment_Status": "informal_employment_status_code",
    "Long_Term_Unemployment_Status": "long_term_unemployment_status_code",
    "Underemployment_Status": "underemployment_status_code",
    "'Not in Education, Employment, or Training' Status": "neet_status_code",
    "Graduate Status": "graduate_status_code",
    "Education Status": "education_status_code",
    "Age Group": "age_group",
    "Hours Worked": "hours_worked",
    "Weight": "survey_weight",
}


def prepare_for_sql(df):
    """
    Renames the transformed DataFrame's columns to their SQL-friendly
    equivalents and downcasts category dtypes to plain values, so the
    result loads cleanly into any SQL engine.
    """
    df = df.rename(columns=SQL_COLUMN_MAP)

    for column in df.select_dtypes(include="category").columns:
        df[column] = df[column].astype(df[column].cat.categories.dtype)

    return df


def load_to_sql(df, engine=None, schema=SCHEMA, table=TABLE, run_schema_setup=True):
    """
    Loads the transformed, validated QLFS DataFrame into the SQL staging
    table, creating the schema/tables first if they don't exist yet.

    Parameters:
    df (pd.DataFrame): The validated, transformed DataFrame to load.
    engine: A SQLAlchemy engine. Defaults to the configured Postgres
        instance (see src/db.py); tests pass an in-memory engine instead.
    run_schema_setup (bool): Runs sql/schema/*.sql before loading, so a
        fresh database is ready to receive data. Safe to call repeatedly:
        the DDL uses CREATE ... IF NOT EXISTS.
    """
    engine = engine or get_engine()
    sql_ready_df = prepare_for_sql(df)

    if run_schema_setup:
        schema_dir = Path(__file__).resolve().parent.parent / "sql" / "schema"
        run_sql_dir(engine, schema_dir)

    load_dataframe(sql_ready_df, table, engine, schema=schema, if_exists="replace")

    print(f"Loaded {len(sql_ready_df)} rows into {schema}.{table}")

    return sql_ready_df

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

