"""
League and season metadata functions for ESPN scraper.

This module contains functions for:
- Getting supported leagues
- Getting available seasons
- Determining current season
- Season date range calculations
"""

import time
from datetime import datetime

from dateutil.relativedelta import relativedelta


def get_leagues():
    """Return a list of supported leagues"""
    return ["mens-college-basketball", "womens-college-basketball"]


def get_yesterday():
    """Get yesterday's date as YYYYMMDD string (latest safe date to scrape)."""
    return datetime.strftime(datetime.now() - relativedelta(days=1), "%Y%m%d")


def get_ncw_groups():
    """Return list of NCAA women's basketball conference groups for scoreboard API"""
    return [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        16,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        29,
        30,
        43,
        44,
        45,
        46,
        47,
        50,
        62,
    ]


def get_current_season_year(league):
    """Get the current season year for a league"""
    if league in get_leagues():
        if datetime.now().month <= 4:
            return datetime.now().year
        else:
            return datetime.now().year + 1


def get_available_seasons(league):
    """Get list of available season years for a league"""
    current_season = get_current_season_year(league)
    if league == "mens-college-basketball":
        return [f"{i:04d}" for i in range(2003, current_season + 1)]
    elif league == "womens-college-basketball":
        return [f"{i:04d}" for i in range(2003, current_season + 1)]
    else:
        raise ValueError("Unknown league for get_available_seasons")


def get_season(league, date_or_season_year):
    """
    Get season year from a date or season year string.

    Args:
        league: League identifier
        date_or_season_year: Either a season year (e.g., "2024") or date (e.g., "20240315")

    Returns:
        Season year as string (e.g., "2024")
    """
    if date_or_season_year in get_available_seasons(league):
        return date_or_season_year
    elif "-" in date_or_season_year:
        date = date_or_season_year.split("-")[0]
    else:
        date = date_or_season_year
    if time.strptime(date, "%Y%m%d").tm_mon > 4:
        season = str(time.strptime(date, "%Y%m%d").tm_year + 1)
    else:
        season = str(time.strptime(date, "%Y%m%d").tm_year)
    return season


def get_season_start_end_dates(league, season_year):
    """
    Get start and end dates for a season.

    Args:
        league: League identifier
        season_year: Season year (e.g., "2024")

    Returns:
        Tuple of (start_date, end_date) as strings in YYYYMMDD format
    """
    if league in get_leagues():
        if season_year in get_available_seasons(league):
            season_year = int(season_year)
            start_date = str(season_year - 1) + "1101"
            end_date = str(season_year) + "0430"
            # Cap at yesterday to avoid incomplete game data
            yesterday = get_yesterday()
            if yesterday < end_date:
                end_date = yesterday
            return start_date, end_date
        else:
            raise ValueError("data is not available for given season_year")
    else:
        raise ValueError("Unknown league for get_all_scoreboard_urls")


def is_scoreboard_season(league, date):
    """
    Determine if a given season should use scoreboard API instead of schedule API.

    Historical note: ESPN changed their API structure for certain seasons.
    This function identifies those special cases.
    """
    if league == "womens-college-basketball" and get_season(league, date) == "2022":
        # return True
        return False
    elif league == "mens-college-basketball" and get_season(league, date) == "2017":
        return False
    else:
        return False
