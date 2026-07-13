from airflow.sdk import dag, task
from pendulum import datetime
from dags.scripts.transaction_generator import generate_fintech_data
from dags.scripts.test_csv_quality import csv_quality_check as run_quality_check
from dags.scripts.s3_upload import upload_file
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

SCRIPTS_DIR = os.path.join(Path(__file__).parent, "scripts")
LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH")

@dag(
    dag_id="fintech_dag",
    start_date=datetime(2026, 7, 12),
    schedule="@daily",
    doc_md=__doc__, 
    catchup=False,
    template_searchpath=[SCRIPTS_DIR],
    default_args={"owner": "Astro", "retries": 3},
)

def fintech_dag():
        @task
        def transaction_generator() -> str:
            generate_fintech_data(LOCAL_FILE_PATH, 2000)
            return LOCAL_FILE_PATH
        
        @task
        def file_quality_check(file_path: str) -> str:
             run_quality_check(file_path)
             return file_path
        
        @task
        def upload_to_s3(file_path: str, ds=None) -> None:
            upload_file(file_path,f"generated_transactions_{ds}.csv")

        execute_query = SQLExecuteQueryOperator(
        task_id="execute_query",
        conn_id ="snowflake_default",
        sql='s3_copy_into_snowflake_stage.sql',
        split_statements=True,
        return_last=False,
        )

        generated_file_path = transaction_generator()
        validated_file = file_quality_check(generated_file_path)
        upload_step = upload_to_s3(validated_file)
        upload_step >> execute_query

fintech_dag()
