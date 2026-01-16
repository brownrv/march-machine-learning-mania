"""
URL building and parsing functions for ESPN scraper.

This module contains pure functions for:
- Building ESPN API URLs (schedule, scoreboard, game, boxscore, playbyplay)
- Parsing URLs to extract metadata (league, data type, IDs)
- Generating URL lists for date ranges and seasons
"""

from datetime import datetime

from dateutil.relativedelta import relativedelta

from .leagues import (
    get_leagues,
    get_ncw_groups,
    get_season_start_end_dates,
    get_yesterday,
    is_scoreboard_season,
)

## Constants
BASE_URL = "https://www.espn.com"


## URL Builders


def get_schedule_url(league, date):
    """Build schedule URL for a specific date"""
    return f"{BASE_URL}/{league}/schedule/_/date/{date}&_xhr=1"


def get_scoreboard_url(league, date, group=None):
    """Build scoreboard URL for a specific date and optional group"""
    if group is not None and is_scoreboard_season(league, date):
        return f"{BASE_URL}/{league}/scoreboard/_/date/{date}/group/{group}&_xhr=1"
    else:
        return f"{BASE_URL}/{league}/scoreboard/_/date/{date}&_xhr=1"


def get_game_url(league, game_id):
    """Build game URL for a specific game ID"""
    return f"{BASE_URL}/{league}/game/_/gameId/{game_id}&_xhr=1"


def get_boxscore_url(league, game_id):
    """Build boxscore URL for a specific game ID"""
    return f"{BASE_URL}/{league}/boxscore/_/gameId/{game_id}&_xhr=1"


def get_playbyplay_url(league, game_id):
    """Build play-by-play URL for a specific game ID"""
    return f"{BASE_URL}/{league}/playbyplay/_/gameId/{game_id}&_xhr=1"


## URL List Generators


def get_all_schedule_urls(league, season_year):
    """Return a list of all schedule URLs for a given league and season year"""
    urls = []
    if league in get_leagues():
        start_date, end_date = get_season_start_end_dates(league, season_year)
        urls = get_range_of_schedule_urls(league, start_date, end_date)
        return urls
    else:
        raise ValueError("Unknown league for get_all_scoreboard_urls")


def get_range_of_schedule_urls(league, start_date, end_date):
    """Return a list of all schedule URLs for a given league and date range.

    Automatically caps end_date at yesterday to avoid scraping incomplete games.
    """
    urls = []
    if league in get_leagues():
        # Cap at yesterday to avoid incomplete game data
        yesterday = get_yesterday()
        if end_date > yesterday:
            end_date = yesterday
        while start_date <= end_date:
            urls.append(get_schedule_url(league, start_date))
            start_date = datetime.strftime(
                datetime.strptime(start_date, "%Y%m%d") + relativedelta(days=1), "%Y%m%d"
            )
        return urls
    else:
        raise ValueError("Unknown league for get_all_scoreboard_urls")


def get_all_scoreboard_urls(league, season_year):
    """Return a list of all scoreboard URLs for a given league and season year"""
    urls = []
    if league in get_leagues():
        start_date, end_date = get_season_start_end_dates(league, season_year)
        urls = get_range_of_scoreboard_urls(league, start_date, end_date)
        return urls
    else:
        raise ValueError("Unknown league for get_all_scoreboard_urls")


def get_range_of_scoreboard_urls(league, start_date, end_date):
    """Return a list of all scoreboard URLs for a given league and date range.

    Automatically caps end_date at yesterday to avoid scraping incomplete games.
    """
    urls = []
    if league in get_leagues():
        # Cap at yesterday to avoid incomplete game data
        yesterday = get_yesterday()
        if end_date > yesterday:
            end_date = yesterday
        while start_date <= end_date:
            for group in get_ncw_groups():
                urls.append(get_scoreboard_url(league, start_date, group))
            start_date = datetime.strftime(
                datetime.strptime(start_date, "%Y%m%d") + relativedelta(days=1), "%Y%m%d"
            )
        return urls
    else:
        raise ValueError("Unknown league for get_range_of_scoreboard_urls")


## URL Parsers


def get_league_from_url(url):
    """Extract league from URL"""
    return url.split(".com/")[1].split("/")[0]


def get_data_type_from_url(url):
    """Guess and return the data_type based on the url"""
    data_type = None
    valid_data_types = ["schedule", "boxscore", "playbyplay", "game", "scoreboard"]
    for valid_data_type in valid_data_types:
        if valid_data_type in url:
            data_type = valid_data_type
            break
    if data_type is None:
        raise ValueError(
            "Unknown data_type for url. Url must contain one of {}".format(valid_data_types)
        )
    return data_type


def get_data_type_id_from_url(url):
    """Extract data type identifier from URL"""
    if "scoreboard" in url:
        return url.split("/")[-3].split("&")[0] + "_" + url.split("/")[-1].split("&")[0]
    else:
        return url.split("/")[-1].split("&")[0]
