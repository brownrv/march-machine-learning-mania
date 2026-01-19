"""
League and season metadata functions for ESPN parser.

This module reuses metadata from espn_scraper and adds parser-specific utilities.
"""

from datetime import datetime


def get_leagues():
    """Return a list of supported leagues."""
    return ["mens-college-basketball", "womens-college-basketball"]


def get_current_season_year(league):
    """Get the current season year for a league."""
    if league in get_leagues():
        if datetime.now().month <= 4:
            return datetime.now().year
        else:
            return datetime.now().year + 1
    raise ValueError(f"Unknown league: {league}")


def get_available_seasons(league):
    """Get list of available season years for a league."""
    current_season = get_current_season_year(league)
    if league in get_leagues():
        return [f"{i:04d}" for i in range(2003, current_season + 1)]
    raise ValueError(f"Unknown league: {league}")


def validate_league(league):
    """Validate that a league is supported."""
    if league not in get_leagues():
        raise ValueError(f"Unknown league: {league}. Supported: {get_leagues()}")
    return league


def validate_season(league, season):
    """Validate that a season is available for a league."""
    available = get_available_seasons(league)
    if season not in available:
        raise ValueError(
            f"Season {season} not available. Available: {available[0]}-{available[-1]}"
        )
    return season
