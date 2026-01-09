"""
Example "Hello World" DAG for March Machine Learning Mania pipeline.

This DAG demonstrates:
- Basic DAG structure
- Daily scheduling
- Importing the kaggle_mmlm package
- Simple logging task
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def log_hello_message():
    """
    Simple task that logs a message and verifies kaggle_mmlm package is available.
    """
    import logging

    # Verify kaggle_mmlm package can be imported
    try:
        import kaggle_mmlm

        logging.info("✓ kaggle_mmlm package successfully imported")
        logging.info(f"Package location: {kaggle_mmlm.__file__}")
    except ImportError as e:
        logging.error(f"Failed to import kaggle_mmlm: {e}")
        raise

    # Log hello message
    logging.info("=" * 50)
    logging.info("Hello from March Machine Learning Mania!")
    logging.info("This is a minimal example DAG.")
    logging.info("=" * 50)

    return "Hello World task completed successfully"


# Define the DAG
with DAG(
    dag_id="example_hello_world",
    description="Minimal example DAG that logs a message and verifies package import",
    schedule="@daily",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example", "hello-world"],
) as dag:
    hello_task = PythonOperator(
        task_id="log_message",
        python_callable=log_hello_message,
    )
