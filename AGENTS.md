# AGENTS.md — Rules for Codex / Claude / other coding agents

This repository is a local-first, open-source data engineering + ML pipeline
(Airflow + scraping + modeling + MLflow). Agents must follow these rules.

## Default workflow: plan → review diff → apply
1) Start by summarizing understanding + proposing a short plan (5–10 bullets).
2) Wait for approval (or explicit request to proceed) before editing files.
3) Make small, reviewable diffs (aim: one logical change-set per iteration).
4) After edits: explain what changed and how to verify (commands).
5) Never claim something works unless you ran the verification step or you clearly say you didn't.

## Guardrails
- Do not add paid services or cloud dependencies (AWS/GCP/Azure) unless explicitly requested.
- Do not add secrets, API keys, or tokens anywhere (code, docs, examples).
- Respect `.gitignore`. Do not commit local artifacts: `.venv/`, `logs/`, `mlruns/`, `mlflow.db`, `data/`, etc.
- Avoid changing Docker/Airflow infra unless asked. If you must, propose the change first.
- Never edit `.env` (use `.env.example` for documentation only).

## Project conventions
### Python / packaging
- Package name: `kaggle_mmlm`
- Source layout: `src/kaggle_mmlm/`
- Dependencies live in `pyproject.toml` (uv-managed). Keep `uv.lock` in sync.
- Prefer Python 3.11 for local dev. Airflow container may run a different Python version.

### Code style
- Use Ruff formatting/linting rules from `pyproject.toml`.
- Add/adjust tests for non-trivial logic changes.
- Prefer small modules with clear responsibilities.

### Data locations (local-only)
- Raw/interim/processed data belongs under `data/` (gitignored).
- Airflow task logs belong under `logs/` (gitignored).
- MLflow tracking uses `mlflow.db` (gitignored).

## Airflow rules
- DAG files should stay orchestration-only (no heavy business logic).
- Business logic belongs in `kaggle_mmlm` modules.
- Keep tasks idempotent: re-runs should not corrupt state.
- Use explicit paths and deterministic outputs.

## MLflow rules
- Tracking backend is local SQLite (`mlflow.db`).
- Tests must not write to `mlflow.db`; use temp dirs/DBs for tests.

## Verification checklist (choose what applies)
- `uv run ruff check .`
- `uv run pytest`
- `uv run python -c "import kaggle_mmlm"`
- Airflow: check scheduler/webserver logs for DAG import errors
- MLflow: log a minimal run and confirm it appears in the UI

## When unsure
If requirements are ambiguous, stop and ask for clarification
after presenting a plan and options.
