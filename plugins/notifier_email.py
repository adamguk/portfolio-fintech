from airflow.providers.standard.operators.email import EmailNotifier

def get_failure_notifier(to_email):
    return EmailNotifier(
        to = to_email,
        subject = (f"Airflow Notification: {ti.dag_name} Failed"),
        html_contents = 
            """
            <h2>Task Failure Notification</h2>
            <p>DAG: {{ti.dag_id}}</p>
            <p>Task: {{ti.task_id}}</p>
            <p>Run Date: {{ds}}</p>
            <p>Log: <a href = "{{ti.log_url}}"<a/>
            """
    )






