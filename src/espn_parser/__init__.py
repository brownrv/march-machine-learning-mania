"""
ESPN Parser - Parse raw ESPN data into structured parquet files.

This package provides tools to parse ESPN basketball data from cached JSON files
and output structured parquet files for analysis.
"""

from espn_parser.parser import (
    parse_all,
    parse_boxscores,
    parse_events,
    parse_games,
    parse_playbyplay,
)
from espn_parser.paths import get_parsed_path, get_raw_path
from espn_parser.reader import (
    list_cached_seasons,
    read_boxscores,
    read_games,
    read_playbyplay,
    read_schedules,
)

__all__ = [
    # Main entry points
    "parse_all",
    "parse_events",
    "parse_games",
    "parse_boxscores",
    "parse_playbyplay",
    # Path utilities
    "get_raw_path",
    "get_parsed_path",
    # Reader utilities
    "read_schedules",
    "read_games",
    "read_boxscores",
    "read_playbyplay",
    "list_cached_seasons",
]
