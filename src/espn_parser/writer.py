"""
Writer module for saving parsed data to parquet files.

This module provides functions to write DataFrames to parquet format.
"""

from pathlib import Path

import pandas as pd

from espn_parser.models import (
    BOXSCORE_COLUMNS,
    EVENT_COLUMNS,
    GAME_COLUMNS,
    PLAY_COLUMNS,
    PLAYER_COLUMNS,
    TEAM_COLUMNS,
    VENUE_COLUMNS,
)
from espn_parser.paths import ensure_parsed_dir, get_parsed_path


def write_parquet(
    df: pd.DataFrame,
    league: str,
    season: str,
    file_name: str,
    base_path: Path | str | None = None,
) -> Path:
    """
    Write a DataFrame to a parquet file.

    Args:
        df: DataFrame to write
        league: League identifier
        season: Season year
        file_name: Output file name (without extension)
        base_path: Base directory for parsed data

    Returns:
        Path to the written file
    """
    ensure_parsed_dir(league, season, base_path)
    file_path = get_parsed_path(league, season, file_name, base_path)
    df.to_parquet(file_path, index=False, engine="pyarrow")
    return file_path


def write_events(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> tuple[Path, int]:
    """
    Write events to parquet.

    Args:
        records: List of event dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Tuple of (path to the written file, record count)
    """
    df = pd.DataFrame(records).reindex(columns=EVENT_COLUMNS)
    path = write_parquet(df, league, season, "events", base_path)
    return path, len(df)


def write_games(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> tuple[Path, int]:
    """
    Write games to parquet.

    Args:
        records: List of game dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Tuple of (path to the written file, record count)
    """
    df = pd.DataFrame(records).reindex(columns=GAME_COLUMNS)
    path = write_parquet(df, league, season, "games", base_path)
    return path, len(df)


def write_teams(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> tuple[Path, int]:
    """
    Write teams to parquet (deduplicated).

    Args:
        records: List of team dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Tuple of (path to the written file, unique team count)
    """
    df = pd.DataFrame(records).reindex(columns=TEAM_COLUMNS)
    # Deduplicate by id, keeping last occurrence (game files have more complete data)
    df = df.drop_duplicates(subset=["id"], keep="last")
    df = df.sort_values("id").reset_index(drop=True)
    path = write_parquet(df, league, season, "teams", base_path)
    return path, len(df)


def write_venues(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> tuple[Path, int]:
    """
    Write venues to parquet (deduplicated).

    Args:
        records: List of venue dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Tuple of (path to the written file, unique venue count)
    """
    if not records:
        df = pd.DataFrame(columns=VENUE_COLUMNS)
    else:
        df = pd.DataFrame(records).reindex(columns=VENUE_COLUMNS)
        # Deduplicate by id, keeping first occurrence
        df = df.drop_duplicates(subset=["id"], keep="first")
        df = df.sort_values("id").reset_index(drop=True)
    path = write_parquet(df, league, season, "venues", base_path)
    return path, len(df)


def write_players(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> tuple[Path, int]:
    """
    Write players to parquet (deduplicated).

    Args:
        records: List of player dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Tuple of (path to the written file, unique player count)
    """
    if not records:
        df = pd.DataFrame(columns=PLAYER_COLUMNS)
    else:
        df = pd.DataFrame(records).reindex(columns=PLAYER_COLUMNS)
        # Deduplicate by aid (athlete ID), keeping first occurrence
        df = df.drop_duplicates(subset=["aid"], keep="first")
        df = df.sort_values("aid").reset_index(drop=True)
    path = write_parquet(df, league, season, "players", base_path)
    return path, len(df)


def write_boxscores(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> tuple[Path, int]:
    """
    Write boxscores to parquet.

    Args:
        records: List of boxscore dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Tuple of (path to the written file, record count)
    """
    if not records:
        df = pd.DataFrame(columns=BOXSCORE_COLUMNS)
    else:
        df = pd.DataFrame(records).reindex(columns=BOXSCORE_COLUMNS)
    path = write_parquet(df, league, season, "boxscores", base_path)
    return path, len(df)


def write_playbyplay(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> tuple[Path, int]:
    """
    Write play-by-play data to parquet.

    Args:
        records: List of play dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Tuple of (path to the written file, record count)
    """
    if not records:
        df = pd.DataFrame(columns=PLAY_COLUMNS)
    else:
        df = pd.DataFrame(records).reindex(columns=PLAY_COLUMNS)
    path = write_parquet(df, league, season, "playbyplay", base_path)
    return path, len(df)
