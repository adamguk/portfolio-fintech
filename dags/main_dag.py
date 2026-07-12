from airflow.sdk import dag, task
from pendulum import datetime
from scripts.transaction_generator import generate_fintech_data
from scripts.s3_upload import upload_file

LOCAL_FILE_PATH = "/tmp/mock_transactions.csv"
BUCKET = "mys3bucket"

@dag(
    dag_id="fintech_dag",
    start_date=datetime(2026, 7, 12),
    schedule="@daily",
    doc_md=__doc__, 
    catchup=False,
    default_args={"owner": "Astro", "retries": 3},
)

def fintech_dag():
    @task
    def transaction_generator() -> str:
        generate_fintech_data(LOCAL_FILE_PATH, 2000)
        return LOCAL_FILE_PATH
    
    @task
    def upload_to_s3(file_path: str) -> None:
        upload_file(LOCAL_FILE_PATH, BUCKET, "generated_transactions.csv")

    @task
    def s3_to_snowflake_stage(s3_bucket: str) -> None:
        pass
        # code to trigger snowflake pulling in the files from s3 using a copy into

    generated_file_path = transaction_generator()
    upload_to_s3(generated_file_path)

fintech_dag()
