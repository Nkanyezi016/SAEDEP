"""
Integration test for the sql/schema and sql/analytics layer.

Runs against an in-memory DuckDB database rather than a live Postgres
server, since DuckDB understands the same plain SQL (CREATE SCHEMA,
CREATE TABLE ... AS SELECT, window-free aggregates) used in sql/. This
gives fast, dependency-free coverage of the actual .sql files without
needing Postgres running in CI.
"""

from pathlib import Path

import pandas as pd
import pytest

sqlalchemy = pytest.importorskip("sqlalchemy")
pytest.importorskip("duckdb_engine")

from sqlalchemy import create_engine, text

from src.db import run_sql_dir
from src.load import load_to_sql

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "sql" / "schema"
ANALYTICS_DIR = REPO_ROOT / "sql" / "analytics"


def make_transformed_sample():
    """
    A small DataFrame already shaped like transform()'s output, covering
    two provinces and a mix of employment statuses, so the analytics
    queries have something meaningful to aggregate.
    """
    return pd.DataFrame({
        "Unique_Questionnaire_Number": [1, 1, 2, 2, 3],
        "Person_Number": [1, 2, 1, 2, 1],
        "Survey_Date": pd.to_datetime(["2026-05-02"] * 5),
        "Province": [7, 7, 1, 1, 7],       # Gauteng, Gauteng, Western Cape, Western Cape, Gauteng
        "Metro_Code": [1, 1, 1, 1, 1],
        "Geo_Type_Code": [1, 1, 1, 1, 1],
        "Stratum": [1, 1, 1, 1, 1],
        "Gender": [1, 2, 1, 2, 1],
        "Age": [29, 45, 34, 22, 50],
        "Marital_Status": [1, 2, 1, 2, 1],
        "Population_Group": [1, 1, 1, 1, 1],
        "Education_Level": [1, 1, 1, 1, 1],
        "Field_of_Study": [1, 1, 1, 1, 1],
        "Attendance_Status": [2, 2, 2, 2, 2],
        "Employment_Status": [1, 2, 1, 1, 2],       # employed/unemployed/employed/employed/unemployed
        "Labour_Force_Status": [1, 2, 1, 1, 2],
        "Unemployment_Status": [None, 3, None, None, 3],
        "Reason_for_Inactivity": [None, None, None, None, None],
        "Industry_Code": [6, None, 9, 9, None],
        "Occupation_Code": [1, None, 2, 2, None],
        "Previous_Industry_Code": [None, 6, None, None, 9],
        "Previous_Occupation_Code": [None, 1, None, None, 2],
        "Sector_Code": [1, None, 1, 2, None],
        "Informal_Employment_Status": [2, None, 2, 1, None],
        "Long_Term_Unemployment_Status": [None, 1, None, None, 2],
        "Underemployment_Status": [2, None, 2, 2, None],
        "'Not in Education, Employment, or Training' Status": [2, 1, 2, 2, 1],
        "Graduate Status": [1, 2, 1, 1, 3],
        "Education Status": [4, 4, 4, 5, 4],
        "Age Group": [3, 4, 3, 2, 5],
        "Hours Worked": [45.0, None, 40.0, 38.0, None],
        "Weight": [1000.0, 1000.0, 2000.0, 2000.0, 1500.0],
    })


@pytest.fixture()
def engine():
    return create_engine("duckdb:///:memory:")


def test_schema_setup_creates_reference_tables(engine):
    run_sql_dir(engine, SCHEMA_DIR)

    provinces = pd.read_sql("SELECT * FROM reference.dim_province", engine)
    assert len(provinces) == 9
    assert set(provinces["province_name"]) >= {"Gauteng", "Western Cape"}

    statuses = pd.read_sql("SELECT * FROM reference.dim_employment_status", engine)
    assert len(statuses) == 4


def test_schema_setup_is_idempotent(engine):
    # Running it twice (as the DAG's schema-setup task will on every run)
    # must not error or duplicate reference rows.
    run_sql_dir(engine, SCHEMA_DIR)
    run_sql_dir(engine, SCHEMA_DIR)

    provinces = pd.read_sql("SELECT * FROM reference.dim_province", engine)
    assert len(provinces) == 9


def test_full_staging_to_analytics_flow(engine):
    df = make_transformed_sample()

    load_to_sql(df, engine=engine)
    run_sql_dir(engine, ANALYTICS_DIR)

    staged = pd.read_sql("SELECT * FROM staging.qlfs_responses", engine)
    assert len(staged) == 5

    unemployment = pd.read_sql(
        "SELECT * FROM analytics.unemployment_rate_by_province ORDER BY province_name",
        engine,
    )
    gauteng = unemployment[unemployment["province_name"] == "Gauteng"].iloc[0]
    # Gauteng rows are index 0 (employed, weight 1000), 1 (unemployed,
    # weight 1000) and 4 (unemployed, weight 1500):
    # unemployment rate = 2500 / 3500 = 71.43%
    assert gauteng["unemployment_rate_pct"] == pytest.approx(71.43, abs=0.01)

    western_cape = unemployment[unemployment["province_name"] == "Western Cape"].iloc[0]
    # Western Cape: both respondents employed -> 0% unemployment
    assert western_cape["unemployment_rate_pct"] == pytest.approx(0.0)

    participation = pd.read_sql(
        "SELECT * FROM analytics.labour_force_participation", engine
    )
    assert len(participation) > 0

    industry = pd.read_sql(
        "SELECT * FROM analytics.industry_sector_breakdown", engine
    )
    # Only employed respondents (3 of 5) should appear.
    assert industry["respondent_count"].sum() == 3

    neet = pd.read_sql("SELECT * FROM analytics.neet_summary", engine)
    assert len(neet) > 0


def test_analytics_can_be_rerun_without_error(engine):
    # DROP TABLE IF EXISTS + CREATE TABLE AS SELECT should tolerate being
    # run repeatedly, since the DAG re-runs analytics on every schedule.
    df = make_transformed_sample()
    load_to_sql(df, engine=engine)

    run_sql_dir(engine, ANALYTICS_DIR)
    run_sql_dir(engine, ANALYTICS_DIR)

    result = pd.read_sql("SELECT * FROM analytics.unemployment_rate_by_province", engine)
    assert len(result) == 2