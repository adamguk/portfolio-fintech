from airflow.sdk import dag, task
from pendulum import datetime
from dags.scripts.transaction_generator import generate_fintech_data
from dags.scripts.test_csv_quality import csv_quality_check as run_quality_check
from dags.scripts.s3_upload import upload_file
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from dotenv import load_dotenv
from pathlib import Path
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import SnowflakeUserPasswordProfileMapping
import os
from plugins.notifier_email import send_failure_email

load_dotenv()

SCRIPTS_DIR = os.path.join(Path(__file__).parent, "scripts")
LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH")
SF_CONN_ID = os.getenv("AIRFLOW_SNOWFLAKE_CONN_ID")
DBT_PROJECT_PATH = f"{os.environ['AIRFLOW_HOME']}/include/dbt/dbt_project"

profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=SnowflakeUserPasswordProfileMapping(
        conn_id=SF_CONN_ID,
        profile_args={"schema": "ANALYTICS"},
    ),
)

@dag(
    dag_id="fintech_dag_v2",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    doc_md=__doc__, 
    catchup=True,
    template_searchpath=[SCRIPTS_DIR],
    max_active_runs=6,

    default_args={
         "owner": "Astro",
          "retries": 3,
          'depends_on_past': True,
          'on_failure_callback': send_failure_email("system-monitor@adamg.io")},
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

        s3_file_check = S3KeySensor(
            task_id="sensor_one_key",
            bucket_name=os.getenv("AWS_S3_BUCKET"),
            bucket_key="generated_transactions_{{ ds }}.csv",
            aws_conn_id="aws_default",
            timeout=600,
            poke_interval=30,
            mode="poke",
        )   

        execute_query = SQLExecuteQueryOperator(
        task_id="execute_query",
        conn_id =SF_CONN_ID,
        sql="populate_snowflake_raw.sql",
        split_statements=True,
        return_last=False,
        )

        transform_data = DbtTaskGroup(
        group_id="transform_data",
        project_config=ProjectConfig(DBT_PROJECT_PATH),
        profile_config=profile_config,
        default_args={"retries": 2},
        )   

        generated_file_path = transaction_generator()
        validated_file = file_quality_check(generated_file_path)
        upload_step = upload_to_s3(validated_file)
        upload_step >> s3_file_check >> execute_query >> transform_data

fintech_dag()
