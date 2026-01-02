from kaggle_mmlm.mlflow_utils import configure_mlflow
import mlflow


def test_mlflow_can_log_run(tmp_path):
    # Use an isolated sqlite DB for the test
    db_path = tmp_path / "mlflow.db"
    mlflow.set_tracking_uri(f"sqlite:///{db_path.as_posix()}")

    mlflow.set_experiment("test_experiment")

    with mlflow.start_run():
        mlflow.log_param("alpha", 0.1)
        mlflow.log_metric("metric", 1.23)

    # Basic assertion: experiment exists
    client = mlflow.tracking.MlflowClient()
    exp = client.get_experiment_by_name("test_experiment")
    assert exp is not None
