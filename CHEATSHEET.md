# March Machine Learning Mania – Dev Cheat Sheet

This file is the single source of truth for getting this repo
back into a working state after a reboot.

---

## 1. Repo Basics

**Repo root:**  
`march-machine-learning-mania/`

**Python package:**  
`kaggle_mmlm` (under `src/`)

**Python version (local dev):**
- Pinned via `.python-version`
- Python **3.11.x**
- Managed by `uv`

---

## 2. Local Python Environment (uv)

### One-time setup (already done)
- uv installed globally
- Python pinned to 3.11
- `.venv/` managed by uv

### After reboot / fresh terminal
Run from **repo root**:

```powershell
uv sync
uv pip install -e .
```

### Verify imports
```powershell
uv run python -c "import kaggle_mmlm; print('ok', kaggle_mmlm.__file__)"
```

---

## 3. Jupyter Notebooks

### Start Jupyter (always from repo root)
```powershell
uv run jupyter notebook
```

In the browser:
- Navigate to `/notebooks`
- Select kernel: **march-mmlm (uv)**

### Sanity check inside a notebook
```python
import sys
from pathlib import Path

print(sys.executable)
print(Path.cwd())
```

Expected:
- Python path points to `.venv`
- Working directory is repo root

---

## 4. MLflow (Local, SQLite backend)

### Configuration (done in code)
MLflow is configured via:
```python
from kaggle_mmlm.mlflow_utils import configure_mlflow
configure_mlflow()
```

This uses:
- SQLite backend
- Database file: `mlflow.db` (repo root)
- Fully local, gitignored

### Typical notebook usage
```python
from kaggle_mmlm.mlflow_utils import configure_mlflow
configure_mlflow()

import mlflow
mlflow.set_experiment("seed_diff_baseline")

with mlflow.start_run():
    mlflow.log_param("alpha", 0.1)
    mlflow.log_metric("brier", 0.123)
```

### Launch MLflow UI
From repo root:

```powershell
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

Open:
- http://127.0.0.1:5000

---

## 5. Tests

### Run all tests
```powershell
uv run pytest
```

### Notes
- MLflow tests use isolated temporary DBs
- No test should write to `mlflow.db`

---

## 6. Airflow (Local, Dockerized)

Airflow runs **only in Docker**.  
Do NOT install Airflow locally with pip.

### Folder
```text
infra/airflow/
```

### Start Airflow
```powershell
cd infra/airflow
docker compose up -d
```

### Initialize / reinitialize metadata DB (safe to rerun)
```powershell
docker compose run --rm airflow-init
```

### Stop Airflow
```powershell
docker compose down
```

### Full reset (nukes DB + logs)
```powershell
docker compose down -v
```

---

## 7. Airflow UI

- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

---

## 8. Custom Airflow Image

Airflow uses a **custom image** that installs `kaggle_mmlm`.

### Dockerfile
```text
infra/airflow/Dockerfile
```

### Rebuild image
```powershell
cd infra/airflow
docker compose build
```

### Verify package inside Airflow
```powershell
docker exec -it airflow-webserver python -c "import kaggle_mmlm; print('ok')"
```

---

## 9. Git Hygiene

### Files tracked
- `pyproject.toml`
- `uv.lock`
- `.python-version`
- `src/`
- `dags/`
- `infra/`

### Files ignored
- `.venv/`
- `data/`
- `mlruns/`
- `mlflow.db`
- `logs/`
- `.env`

---

## 10. Common Commands (Quick Reference)

### Repo root
```powershell
uv sync
uv pip install -e .
uv run pytest
uv run jupyter notebook
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

### Airflow
```powershell
cd infra/airflow
docker compose up -d
docker compose down
docker compose build
docker compose run --rm airflow-init
```

---

## 11. Mental Model (Important)

- **Local dev & ML:** Python 3.11 (uv)
- **Airflow runtime:** Python 3.12 (Docker image)
- These are intentionally different
- Airflow orchestrates; your package does the work

---

## 12. If Something Breaks

1. Restart terminal
2. `uv sync`
3. `uv pip install -e .`
4. Restart Jupyter kernel
5. Restart Airflow containers

If MLflow errors look filesystem-related:
- Delete `mlruns/` or `mlflow.db`
- Restart kernel
- Re-run `configure_mlflow()`

---




