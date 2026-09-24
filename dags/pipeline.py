from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from src.extract import extract_data
from src.transform import transform_data
from src.validate import validate
from src.load import load_data

RAW_DATA_PATH = "data/raw/QLFS202602.csv"
PROCESSED_DATA_PATH = "data/processed/QLFS202602_processed.csv"

def extract_task():
    extract_data(RAW_DATA_PATH)

def transform_task():
    labor_data = transform_data(RAW_DATA_PATH)
    labor_data.to_pickle("tmp/qlfs_transformed.pkl")  # Save the transformed data to a temporary file

def validate_task():
    import pandas as pd
    labor_data = pd.read_pickle("tmp/qlfs_transformed.pkl")  # Load the transformed data from the temporary file
    validate(labor_data)

def load_task():
    import pandas as pd
    labor_data = pd.read_pickle("tmp/qlfs_transformed.pkl")  # Load the transformed data from the temporary file
    load_data(labor_data, PROCESSED_DATA_PATH)


with DAG( dag_id="qlfs_data_pipeline", 
         start_date=datetime(2026, 9, 24), 
         schedule=None, 
         catchup=False, 
         tags=["QLFS", "data-engineering"], 
         ) as dag:

            extract = PythonOperator(
                  task_id = "extract_qlfs_data",
                  python_callable = extract_task,
            )

            transform = PythonOperator(
                  task_id = "transform_qlfs_data",
                  python_callable = transform_task,
            )

            validate = PythonOperator(
                  task_id = "validate_qlfs_data",
                  python_callable = validate_task,
            )

            load = PythonOperator(
                  task_id = "load_qlfs_data",
                  python_callable = load_task,
            )

            extract >> transform >> validate >> load