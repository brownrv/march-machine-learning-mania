"""
Reader module for loading raw ESPN JSON data.

This module provides functions to read cached JSON files from the raw data directory.
"""

import json
from pathlib import Path
from typing import Any, Generator

from espn_parser.paths import list_raw_files


def read_json(file_path: Path) -> dict[str, Any] | list[Any] | None:
    """
    Read a JSON file and return its contents.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data, or None if file doesn't exist or is invalid
    """
    if not file_path.exists():
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Skip files that contain error messages
            if isinstance(data, dict) and "error_msg" in data:
                return None
            return data
    except (json.JSONDecodeError, OSError):
        return None


def read_schedules(
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Generator[tuple[str, list[dict[str, Any]]], None, None]:
    """
    Read all schedule files for a league and season.

    Args:
        league: League identifier
        season: Season year
        base_path: Base directory for raw data

    Yields:
        Tuples of (date_string, events_list) for each schedule file
    """
    files = list_raw_files(league, season, "schedule", base_path)
    for file_path in files:
        date_str = file_path.stem  # e.g., "20231106"
        data = read_json(file_path)
        if data is not None and isinstance(data, list):
            yield date_str, data


def read_games(
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Generator[tuple[str, dict[str, Any]], None, None]:
    """
    Read all game files for a league and season.

    Args:
        league: League identifier
        season: Season year
        base_path: Base directory for raw data

    Yields:
        Tuples of (game_id, game_data) for each game file
    """
    files = list_raw_files(league, season, "game", base_path)
    for file_path in files:
        game_id = file_path.stem
        data = read_json(file_path)
        if data is not None and isinstance(data, dict):
            yield game_id, data


def read_boxscores(
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Generator[tuple[str, dict[str, Any]], None, None]:
    """
    Read all boxscore files for a league and season.

    Args:
        league: League identifier
        season: Season year
        base_path: Base directory for raw data

    Yields:
        Tuples of (game_id, boxscore_data) for each boxscore file
    """
    files = list_raw_files(league, season, "boxscore", base_path)
    for file_path in files:
        game_id = file_path.stem
        data = read_json(file_path)
        if data is not None and isinstance(data, dict):
            yield game_id, data


def read_playbyplay(
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Generator[tuple[str, dict[str, Any]], None, None]:
    """
    Read all play-by-play files for a league and season.

    Args:
        league: League identifier
        season: Season year
        base_path: Base directory for raw data

    Yields:
        Tuples of (game_id, playbyplay_data) for each file
    """
    files = list_raw_files(league, season, "playbyplay", base_path)
    for file_path in files:
        game_id = file_path.stem
        data = read_json(file_path)
        if data is not None and isinstance(data, dict):
            yield game_id, data


def list_cached_seasons(
    league: str,
    base_path: Path | str | None = None,
) -> list[str]:
    """
    List all seasons that have cached data for a league.

    Args:
        league: League identifier
        base_path: Base directory for raw data

    Returns:
        Sorted list of season years that have data
    """
    from espn_parser.paths import DEFAULT_RAW_BASE

    base = Path(base_path) if base_path else DEFAULT_RAW_BASE
    league_path = base / league
    if not league_path.exists():
        return []

    seasons = []
    for item in league_path.iterdir():
        if item.is_dir() and item.name.isdigit() and len(item.name) == 4:
            seasons.append(item.name)

    return sorted(seasons)


def count_files(
    league: str,
    season: str,
    data_type: str,
    base_path: Path | str | None = None,
) -> int:
    """
    Count the number of files for a given data type.

    Args:
        league: League identifier
        season: Season year
        data_type: Type of data
        base_path: Base directory

    Returns:
        Number of JSON files
    """
    return len(list_raw_files(league, season, data_type, base_path))
