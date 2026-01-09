"""
ESPN Basketball Scraper

A Python package for scraping college basketball data from ESPN's JSON API.

Main entry points:
- get_all(): Fetch all data for a league/season/date
- get_missing(): Check cache and fetch missing data
- get_url(): Fetch single URL (cache-aware)
- get_schedule(): Get schedule URLs for a league/date

For internal use:
- Various URL builders, parsers, and utilities in submodules
"""

# Public API exports
# Legacy imports for backward compatibility (utility functions)
import json
import time

from .leagues import get_available_seasons, get_leagues, get_season
from .scraper import get_all, get_missing, get_schedule, get_url
from .urls import (
    get_boxscore_url,
    get_game_url,
    get_playbyplay_url,
    get_schedule_url,
    get_scoreboard_url,
)


def ppjson(data):
    """Pretty-print JSON data (legacy utility function)"""
    print(json.dumps(data, indent=2, sort_keys=True))


def timing(f):
    """Decorator to time function execution (legacy utility function)"""

    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print("{:s} function took {:.3f} ms".format(f.__name__, (time2 - time1) * 1000.0))

        return ret

    return wrap


__all__ = [
    # Main entry points
    "get_all",
    "get_missing",
    "get_url",
    "get_schedule",
    # League/season utilities
    "get_leagues",
    "get_available_seasons",
    "get_season",
    # URL builders
    "get_schedule_url",
    "get_scoreboard_url",
    "get_game_url",
    "get_boxscore_url",
    "get_playbyplay_url",
    # Legacy utilities
    "ppjson",
    "timing",
]
