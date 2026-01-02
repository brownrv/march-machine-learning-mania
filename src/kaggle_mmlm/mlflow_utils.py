from __future__ import annotations

from pathlib import Path
import mlflow


def _find_repo_root(start: Path | None = None) -> Path:
    p = (start or Path.cwd()).resolve()
    for parent in [p, *p.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback: assume current working directory
    return p


def configure_mlflow(repo_root: Path | None = None) -> None:
    root = repo_root or _find_repo_root()
    db_path = root / "mlflow.db"
    mlflow.set_tracking_uri(f"sqlite:///{db_path.as_posix()}")
