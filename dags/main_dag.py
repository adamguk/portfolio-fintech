from airflow.sdk import dag, task
from pendulum import datetime
from scripts.transaction_generator import generate_fintech_data
from scripts.s3_upload import upload_file
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

LOCAL_FILE_PATH = "/tmp/mock_transactions.csv"
BUCKET = "mys3bucket"

@dag(
    dag_id="fintech_dag",
    start_date=datetime(2026, 7, 12),
    schedule="@daily",
    doc_md=__doc__, 
    catchup=False,
    template_searchpath="/opt/airflow/scripts",
    default_args={"owner": "Astro", "retries": 3},
)

def fintech_dag():
        @task
        def transaction_generator() -> str:
            generate_fintech_data(LOCAL_FILE_PATH, 2000)
            return LOCAL_FILE_PATH
        
        @task
        def upload_to_s3(file_path: str, ds=None) -> None:
            upload_file(file_path, BUCKET, f"generated_transactions_{ds}.csv")

        execute_query = SQLExecuteQueryOperator(
        task_id="execute_query",
        conn_id ="snowflake_default",
        sql='s3_copy_into_snowflake_stage.sql',
        split_statements=True,
        return_last=False,
        )

        generated_file_path = transaction_generator()
        upload_step = upload_to_s3(generated_file_path)
        upload_step >> execute_query

fintech_dag()
