# march-machine-learning-mania
Forecast College Basketball Tournaments

## About

Local-first data engineering + ML pipeline for the [March Machine Learning Mania](https://www.kaggle.com/competitions/march-machine-learning-mania-2024) Kaggle competition. This project predicts NCAA tournament outcomes using:
- Team rating systems (Elo, Chessmetrics)
- Betting odds data (scraped from BetExplorer)
- Historical tournament data
- MLflow experiment tracking
- Airflow orchestration (Docker-based)

All processing runs locally—no cloud dependencies required.

---

## Quick Start

### Prerequisites
- Python 3.11+ (managed via `uv`)
- Docker (for Airflow)

### 1. Set up Python environment
```bash
# From repo root
uv sync
uv pip install -e .

# Verify installation
uv run python -c "import kaggle_mmlm; print('✓ Package installed')"
```

### 2. Start Jupyter notebooks
```bash
uv run jupyter notebook
# Navigate to /notebooks in browser
```

### 3. Launch MLflow UI (optional)
```bash
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
# Open http://127.0.0.1:5000
```

### 4. Start Airflow (optional)
```bash
cd infra/airflow
docker compose up -d
# Access UI at http://localhost:8080 (user: airflow / pass: airflow)
```

**For detailed setup, troubleshooting, and daily workflows, see [CHEATSHEET.md](CHEATSHEET.md).**

---

## Project Structure

```
src/kaggle_mmlm/       # Core Python package (data processing, scraping, utils)
notebooks/             # Jupyter notebooks (EDA, modeling, submissions)
dags/                  # Airflow DAGs (orchestration)
infra/airflow/         # Docker-based Airflow setup
data/                  # Local data storage (gitignored)
tests/                 # Pytest tests
```

---

## Key Tools

- **uv** - Python dependency management
- **Airflow** - Workflow orchestration (Dockerized)
- **MLflow** - Experiment tracking (SQLite backend)
- **Jupyter** - Interactive analysis
- **Selenium + pandas** - Web scraping & data manipulation
- **pytest + Ruff** - Testing & linting

---

## Resources

- [CHEATSHEET.md](CHEATSHEET.md) - Comprehensive setup & daily command reference
- [AGENTS.md](AGENTS.md) - Guidelines for AI coding assistants