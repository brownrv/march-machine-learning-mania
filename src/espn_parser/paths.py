"""
Path builders for ESPN parser.

This module provides functions to construct paths for:
- Raw ESPN data input (data/raw/espn/)
- Parsed parquet output (data/parsed/espn/)
"""

from pathlib import Path

# Default base directories
DEFAULT_RAW_BASE = Path("data/raw/espn")
DEFAULT_PARSED_BASE = Path("data/parsed/espn")

# Data types available in raw data
RAW_DATA_TYPES = ["schedule", "game", "boxscore", "playbyplay"]

# Output parquet file names
PARSED_FILES = [
    "events",
    "games",
    "teams",
    "players",
    "venues",
    "boxscores",
    "playbyplay",
]


def get_raw_path(
    league: str,
    season: str,
    data_type: str | None = None,
    file_id: str | None = None,
    base_path: Path | str | None = None,
) -> Path:
    """
    Build path to raw ESPN data.

    Args:
        league: League identifier (e.g., "mens-college-basketball")
        season: Season year (e.g., "2024")
        data_type: Type of data ("schedule", "game", "boxscore", "playbyplay")
        file_id: File identifier (date for schedule, game_id for others)
        base_path: Base directory (default: data/raw/espn)

    Returns:
        Path to the raw data directory or file

    Examples:
        get_raw_path("mens-college-basketball", "2024")
        # -> data/raw/espn/mens-college-basketball/2024

        get_raw_path("mens-college-basketball", "2024", "schedule")
        # -> data/raw/espn/mens-college-basketball/2024/schedule

        get_raw_path("mens-college-basketball", "2024", "game", "401573353")
        # -> data/raw/espn/mens-college-basketball/2024/game/401573353.json
    """
    base = Path(base_path) if base_path else DEFAULT_RAW_BASE
    path = base / league / season

    if data_type:
        if data_type not in RAW_DATA_TYPES:
            raise ValueError(f"Invalid data_type: {data_type}. Must be one of {RAW_DATA_TYPES}")
        path = path / data_type

    if file_id:
        if not data_type:
            raise ValueError("data_type is required when file_id is specified")
        path = path / f"{file_id}.json"

    return path


def get_parsed_path(
    league: str,
    season: str,
    file_name: str | None = None,
    base_path: Path | str | None = None,
) -> Path:
    """
    Build path to parsed parquet output.

    Args:
        league: League identifier (e.g., "mens-college-basketball")
        season: Season year (e.g., "2024")
        file_name: Parquet file name without extension (e.g., "games", "boxscores")
        base_path: Base directory (default: data/parsed/espn)

    Returns:
        Path to the parsed data directory or file

    Examples:
        get_parsed_path("mens-college-basketball", "2024")
        # -> data/parsed/espn/mens-college-basketball/2024

        get_parsed_path("mens-college-basketball", "2024", "games")
        # -> data/parsed/espn/mens-college-basketball/2024/games.parquet
    """
    base = Path(base_path) if base_path else DEFAULT_PARSED_BASE
    path = base / league / season

    if file_name:
        if file_name not in PARSED_FILES:
            raise ValueError(f"Invalid file_name: {file_name}. Must be one of {PARSED_FILES}")
        path = path / f"{file_name}.parquet"

    return path


def list_raw_files(
    league: str,
    season: str,
    data_type: str,
    base_path: Path | str | None = None,
) -> list[Path]:
    """
    List all raw JSON files for a given league, season, and data type.

    Args:
        league: League identifier
        season: Season year
        data_type: Type of data
        base_path: Base directory

    Returns:
        Sorted list of Path objects to JSON files
    """
    dir_path = get_raw_path(league, season, data_type, base_path=base_path)
    if not dir_path.exists():
        return []
    return sorted(dir_path.glob("*.json"))


def ensure_parsed_dir(
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Path:
    """
    Ensure the parsed output directory exists.

    Args:
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Path to the created directory
    """
    dir_path = get_parsed_path(league, season, base_path=base_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
