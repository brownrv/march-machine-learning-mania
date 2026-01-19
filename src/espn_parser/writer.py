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
) -> Path:
    """
    Write events to parquet.

    Args:
        records: List of event dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Path to the written file
    """
    df = pd.DataFrame(records)
    # Reorder columns and handle missing
    for col in EVENT_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[EVENT_COLUMNS]
    return write_parquet(df, league, season, "events", base_path)


def write_games(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Path:
    """
    Write games to parquet.

    Args:
        records: List of game dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Path to the written file
    """
    df = pd.DataFrame(records)
    for col in GAME_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[GAME_COLUMNS]
    return write_parquet(df, league, season, "games", base_path)


def write_teams(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Path:
    """
    Write teams to parquet (deduplicated).

    Args:
        records: List of team dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Path to the written file
    """
    df = pd.DataFrame(records)
    for col in TEAM_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[TEAM_COLUMNS]
    # Deduplicate by id, keeping first occurrence
    df = df.drop_duplicates(subset=["id"], keep="first")
    df = df.sort_values("id").reset_index(drop=True)
    return write_parquet(df, league, season, "teams", base_path)


def write_venues(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Path:
    """
    Write venues to parquet (deduplicated).

    Args:
        records: List of venue dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Path to the written file
    """
    df = pd.DataFrame(records)
    if df.empty:
        # Create empty DataFrame with correct columns
        df = pd.DataFrame(columns=VENUE_COLUMNS)
    else:
        for col in VENUE_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[VENUE_COLUMNS]
        # Deduplicate by id, keeping first occurrence
        df = df.drop_duplicates(subset=["id"], keep="first")
        df = df.sort_values("id").reset_index(drop=True)
    return write_parquet(df, league, season, "venues", base_path)


def write_players(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Path:
    """
    Write players to parquet (deduplicated).

    Args:
        records: List of player dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Path to the written file
    """
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=PLAYER_COLUMNS)
    else:
        for col in PLAYER_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[PLAYER_COLUMNS]
        # Deduplicate by aid (athlete ID), keeping first occurrence
        df = df.drop_duplicates(subset=["aid"], keep="first")
        df = df.sort_values("aid").reset_index(drop=True)
    return write_parquet(df, league, season, "players", base_path)


def write_boxscores(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Path:
    """
    Write boxscores to parquet.

    Args:
        records: List of boxscore dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Path to the written file
    """
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=BOXSCORE_COLUMNS)
    else:
        for col in BOXSCORE_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[BOXSCORE_COLUMNS]
    return write_parquet(df, league, season, "boxscores", base_path)


def write_playbyplay(
    records: list[dict],
    league: str,
    season: str,
    base_path: Path | str | None = None,
) -> Path:
    """
    Write play-by-play data to parquet.

    Args:
        records: List of play dictionaries
        league: League identifier
        season: Season year
        base_path: Base directory

    Returns:
        Path to the written file
    """
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=PLAY_COLUMNS)
    else:
        for col in PLAY_COLUMNS:
            if col not in df.columns:
                df[col] = None
        df = df[PLAY_COLUMNS]
    return write_parquet(df, league, season, "playbyplay", base_path)
