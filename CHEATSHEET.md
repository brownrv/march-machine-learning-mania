# March Machine Learning Mania – Dev Cheat Sheet

This file is the **single source of truth** for getting this repo  
back into a working state after a reboot.

---

## 0. Prerequisites (Read First)

### Docker Desktop
🚨 **Docker Desktop must be running before starting Airflow.**

- Start Docker Desktop manually
- Wait until it shows **“Docker Engine running”**
- Only then run any `docker compose` commands

If Docker Desktop is not running:
- Airflow containers will fail silently or hang
- Volume mounts may not initialize correctly

---

## 1. Repo Basics

**Repo root:**  
`march-machine-learning-mania/`

**Python packages (under `src/`):**
- `kaggle_mmlm` – modeling, MLflow, competition logic
- `espn_scraper` – ESPN data ingestion (CLI + Python API)

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
uv run python -c "import kaggle_mmlm, espn_scraper; print('ok')"
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

## 5. ESPN Scraper (Local)

**Package:**
`src/espn_scraper/`

**Unit of work:**
- **One day of games** (or season, date range)

**Cache model:**
- Raw JSON responses
- Deterministic folder layout
- Safe to re-run (idempotent, skips cached files)

**Performance:**
- Concurrent fetching (3 workers)
- Connection pooling with retry logic
- ~5-8 min for a full day vs ~37 min before optimization

### CLI usage

```powershell
# Show commands
espn-scraper --help
espn-scraper <command> --help
```

#### Single date
```powershell
espn-scraper get-all `
  --league mens-college-basketball `
  --date 20240101 `
  --cache-dir data/raw/espn
```

#### Date range
```powershell
espn-scraper get-all `
  --league mens-college-basketball `
  --date 20241101-20241231 `
  --cache-dir data/raw/espn
```

#### Full season
```powershell
espn-scraper get-all `
  --league mens-college-basketball `
  --season 2024 `
  --cache-dir data/raw/espn
```

#### Multiple seasons (year range)
```powershell
espn-scraper get-all `
  --league mens-college-basketball `
  --season 2020-2024 `
  --cache-dir data/raw/espn
```

#### Both leagues at once
```powershell
espn-scraper get-all `
  --league both `
  --date 20240315 `
  --cache-dir data/raw/espn
```

#### Resume interrupted scrape (fetch missing only)
```powershell
espn-scraper get-missing `
  --league both `
  --season 2020-2024 `
  --cache-dir data/raw/espn
```

### Python API
```python
from espn_scraper import get_all, get_missing

# Single date
get_all("mens-college-basketball", "20240101", "data/raw/espn")

# Full season
get_all("mens-college-basketball", "2024", "data/raw/espn")

# Date range
get_all("womens-college-basketball", "20241101-20241231", "data/raw/espn")

# Resume interrupted scrape
get_missing("mens-college-basketball", "2024", "data/raw/espn")
```

### Cache contract (important)
```text
data/raw/espn/
  <league>/
    <season>/
      schedule/
        YYYYMMDD.json
      game/
        <game_id>.json
      boxscore/
        <game_id>.json
      playbyplay/
        <game_id>.json
```

### Logging
Logs are written to `logs/espn-scraper.log` by default (gitignored).

```powershell
# Default logging (warnings only to console, INFO to file)
espn-scraper get-all -l mens-college-basketball -s 2024

# Verbose console output (INFO level)
espn-scraper -v get-all -l mens-college-basketball -s 2024

# Debug output (all fetch attempts)
espn-scraper -vv get-all -l mens-college-basketball -s 2024

# Custom log file
espn-scraper --log-file logs/2024-scrape.log get-all -l mens-college-basketball -s 2024
```

Log levels:
- `WARNING`: Skipped URLs (errors, invalid JSON, connection issues)
- `INFO`: OK fetches, progress summaries, game counts
- `DEBUG`: All fetch attempts, timing details

### Retry & Rate Limiting
- Default delay: 1.0 second between requests
- 5 retries with exponential backoff (2s, 4s, 8s, 16s, 32s)
- Handles 429, 500, 502, 503, 504 errors automatically
- Gracefully handles connection errors (ChunkedEncodingError, timeouts)
- To adjust delay, edit `REQUEST_DELAY` in `src/espn_scraper/client.py`

---

## 6. Tests

### Run all tests
```powershell
uv run pytest
```

### ESPN scraper tests only
```powershell
uv run pytest tests/espn_scraper
```

### Notes
- ESPN tests use fixtures + monkeypatching
- No network calls during tests
- MLflow tests use isolated temporary DBs
- No test should write to `mlflow.db`

---

## 7. Airflow (Local, Dockerized)

⚠️ **Docker Desktop must be running first** (see Section 0).

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

## 8. Airflow UI

- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

---

## 9. Custom Airflow Image

Airflow uses a **custom image** that installs:
- `kaggle_mmlm`
- `espn_scraper`

### Dockerfile
```text
infra/airflow/Dockerfile
```

### Rebuild image
```powershell
cd infra/airflow
docker compose build
```

### Verify packages inside Airflow
```powershell
docker exec -it airflow-webserver python -c "import kaggle_mmlm, espn_scraper; print('ok')"
```

---

## 10. Git Hygiene

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

## 11. Common Commands (Quick Reference)

### Repo root
```powershell
uv sync
uv pip install -e .
uv run pytest
uv run jupyter notebook
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db
```

### ESPN scraper
```powershell
# Single date
espn-scraper get-all --league mens-college-basketball --date 20241104 --cache-dir data/raw/espn

# Both leagues, multiple seasons
espn-scraper get-all --league both --season 2020-2024 --cache-dir data/raw/espn

# Resume interrupted scrape
espn-scraper get-missing --league both --season 2024 --cache-dir data/raw/espn
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

## 12. Mental Model (Important)

- **Local dev & ML:** Python 3.11 (uv)
- **Airflow runtime:** Python 3.12 (Docker image)
- These are intentionally different
- Airflow orchestrates; your packages do the work
- ESPN scraper = ingestion (bronze)
- Parsing / parquet = next pipeline stage (silver)

---

## 13. If Something Breaks

1. Restart terminal
2. Ensure **Docker Desktop is running**
3. `uv sync`
4. `uv pip install -e .`
5. Restart Jupyter kernel
6. Restart Airflow containers

If MLflow errors look filesystem-related:
- Delete `mlruns/` or `mlflow.db`
- Restart kernel
- Re-run `configure_mlflow()`
