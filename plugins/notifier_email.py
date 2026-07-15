from airflow.providers.smtp.notifications.smtp import send_smtp_notification

def send_failure_email(to_email: str):
    return send_smtp_notification(
        from_email="system-monitor@adamg.io",
        to=to_email,
        subject="Airflow Notification: {{ ti.dag_id }} Failed",
        html_content="""
        <h2>Task Failure Notification</h2>
        <p><b>DAG:</b> {{ ti.dag_id }}</p>
        <p><b>Task:</b> {{ ti.task_id }}</p>
        <p><b>Run Date:</b> {{ ds }}</p>
        <p><b>Log:</b> <a href="{{ ti.log_url }}">View Airflow Logs</a></p>
        """
    )