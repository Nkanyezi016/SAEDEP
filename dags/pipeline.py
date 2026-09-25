from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.extract import extract_data
from src.transform import transform
from src.validate import validate
from src.load import load_data, load_to_sql
from src.db import get_engine, run_sql_dir

RAW_DATA_PATH = "data/raw/QLFS202602.csv"
PROCESSED_DATA_PATH = "data/processed/QLFS202602_processed.csv"

# Airflow tasks run in separate processes/containers, so state can't be
# passed in memory between them; the transformed DataFrame is handed off
# via a pickle file on the shared volume instead. Keeping it under
# AIRFLOW_HOME (rather than a bare relative "tmp/") means it lands
# somewhere writable and consistent regardless of the worker's cwd.
TMP_DIR = Path("/opt/airflow/tmp")
TRANSFORMED_PATH = TMP_DIR / "qlfs_transformed.pkl"

REPO_ROOT = Path(__file__).resolve().parent.parent
SQL_SCHEMA_DIR = REPO_ROOT / "sql" / "schema"
SQL_ANALYTICS_DIR = REPO_ROOT / "sql" / "analytics"


def setup_schema_task():
    """Creates the staging/reference/analytics schemas and reference
    tables. Safe to run on every schedule: the DDL is idempotent."""
    engine = get_engine()
    run_sql_dir(engine, SQL_SCHEMA_DIR)


def extract_task():
    # Runs extract on its own (separately from transform_task, which
    # re-extracts) purely so a broken/missing source file fails fast at
    # the extract step rather than surfacing downstream in transform.
    raw_data = extract_data(RAW_DATA_PATH)
    print(f"Extracted {len(raw_data)} rows from {RAW_DATA_PATH}")


def transform_task():
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    raw_data = extract_data(RAW_DATA_PATH)
    labor_data = transform(raw_data)
    labor_data.to_pickle(TRANSFORMED_PATH)


def validate_task():
    import pandas as pd
    labor_data = pd.read_pickle(TRANSFORMED_PATH)
    validate(labor_data)


def load_task():
    import pandas as pd
    labor_data = pd.read_pickle(TRANSFORMED_PATH)

    # Keep a flat-file snapshot of the processed data alongside the SQL
    # load, useful for quick inspection without needing a DB connection.
    load_data(labor_data, PROCESSED_DATA_PATH)

    engine = get_engine()
    load_to_sql(labor_data, engine=engine, run_schema_setup=False)


def run_analytics_task():
    engine = get_engine()
    run_sql_dir(engine, SQL_ANALYTICS_DIR)


with DAG(
    dag_id="qlfs_data_pipeline",
    start_date=datetime(2026, 9, 24),
    schedule=None,
    catchup=False,
    tags=["QLFS", "data-engineering"],
) as dag:

    setup_schema = PythonOperator(
        task_id="setup_sql_schema",
        python_callable=setup_schema_task,
    )

    extract = PythonOperator(
        task_id="extract_qlfs_data",
        python_callable=extract_task,
    )

    transform_op = PythonOperator(
        task_id="transform_qlfs_data",
        python_callable=transform_task,
    )

    validate_op = PythonOperator(
        task_id="validate_qlfs_data",
        python_callable=validate_task,
    )

    load = PythonOperator(
        task_id="load_qlfs_data",
        python_callable=load_task,
    )

    run_analytics = PythonOperator(
        task_id="run_sql_analytics",
        python_callable=run_analytics_task,
    )

    setup_schema >> extract >> transform_op >> validate_op >> load >> run_analytics
