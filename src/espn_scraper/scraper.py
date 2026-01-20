"""
Core scraping orchestration logic for ESPN scraper.

This module contains the main entry points:
- get_all(): Fetch all data for a league/season/date
- get_missing(): Check cache and fetch missing data
- get_url(): Fetch single URL (cache-aware)
- get_schedule(): Get schedule URLs for a league/date
"""

import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

from .cache import get_cached, get_filename, is_cached, write_cache
from .client import DEFAULT_USER_AGENT, get_multiple_json, get_new_json
from .leagues import (
    get_available_seasons,
    get_ncw_groups,
    get_season,
    get_yesterday,
    is_scoreboard_season,
)
from .urls import (
    get_all_schedule_urls,
    get_all_scoreboard_urls,
    get_boxscore_url,
    get_data_type_from_url,
    get_data_type_id_from_url,
    get_game_url,
    get_league_from_url,
    get_playbyplay_url,
    get_range_of_schedule_urls,
    get_range_of_scoreboard_urls,
    get_schedule_url,
    get_scoreboard_url,
)


def get_schedule(league, date_or_season_year):
    """
    Return a list of schedule URLs for a league or date(s).

    Automatically skips dates >= today to avoid scraping incomplete games.

    Args:
        league: League identifier
        date_or_season_year: Can be:
            - Season year (e.g., "2024") - returns all URLs for that season
            - Date range (e.g., "20240101-20240331") - returns URLs for date range
            - Single date (e.g., "20240315") - returns URL(s) for that date

    Returns:
        list: List of schedule/scoreboard URLs
    """
    urls = []

    season = get_season(league, date_or_season_year)
    # entire season
    if date_or_season_year in get_available_seasons(league):
        if is_scoreboard_season(league, date_or_season_year):
            urls = get_all_scoreboard_urls(league, date_or_season_year)
        else:
            urls = get_all_schedule_urls(league, date_or_season_year)
    # date range
    elif "-" in date_or_season_year:
        if is_scoreboard_season(league, season):
            urls = get_range_of_scoreboard_urls(
                league,
                date_or_season_year.split("-")[0],
                date_or_season_year.split("-")[1],
            )
        else:
            urls = get_range_of_schedule_urls(
                league,
                date_or_season_year.split("-")[0],
                date_or_season_year.split("-")[1],
            )
    # single date
    else:
        # Skip today and future dates
        yesterday = get_yesterday()
        if date_or_season_year > yesterday:
            logger.info("Skipping %s (today or future date)", date_or_season_year)
            return []
        if is_scoreboard_season(league, season):
            for group in get_ncw_groups():
                urls.append(get_scoreboard_url(league, date_or_season_year, group))
        else:
            urls.append(get_schedule_url(league, date_or_season_year))

    return urls


def get_cached_url(
    url,
    league,
    season,
    data_type,
    data_type_id,
    cached_path,
    headers=None,
):
    """
    Retrieve data from cache or fetch from ESPN API.

    Args:
        url: URL to fetch
        league: League identifier
        season: Season year
        data_type: Type of data (schedule, scoreboard, game, boxscore, playbyplay)
        data_type_id: Identifier extracted from URL
        cached_path: Base cache directory path
        headers: HTTP headers for request

    Returns:
        dict: Parsed data from cache or API
    """
    if headers is None:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
    if cached_path:
        filename = get_filename(cached_path, league, season, data_type, url)
        data = get_cached(filename)
    else:
        data = None
    if data is None:
        data = get_new_json(url, headers)
        if "error_msg" not in data:
            if data_type == "schedule":
                data = data["page"]["content"]["events"][data_type_id]
            elif data_type == "scoreboard":
                data = data["page"]["content"]["scoreboard"]["evts"]
            elif data_type in ["boxscore", "playbyplay", "game"]:
                data = data["page"]["content"]["gamepackage"]

        if cached_path:
            write_cache(filename, data)

    return data


def overwrite_cached_url(
    url,
    league,
    season,
    data_type,
    data_type_id,
    cached_path,
    headers=None,
):
    """
    Force re-fetch data from ESPN API and overwrite cache.

    Args:
        url: URL to fetch
        league: League identifier
        season: Season year
        data_type: Type of data (schedule, scoreboard, game, boxscore, playbyplay)
        data_type_id: Identifier extracted from URL
        cached_path: Base cache directory path
        headers: HTTP headers for request

    Returns:
        dict: Parsed data from API
    """
    if headers is None:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
    filename = get_filename(cached_path, league, season, data_type, url)
    data = get_new_json(url, headers)
    if "error_msg" not in data:
        if data_type == "schedule":
            data = data["page"]["content"]["events"][data_type_id]
        elif data_type == "scoreboard":
            data = data["page"]["content"]["scoreboard"]["evts"]
        elif data_type in ["boxscore", "playbyplay", "game"]:
            data = data["page"]["content"]["gamepackage"]

    write_cache(filename, data)

    return data


def get_url(url, season, cached_path=None):
    """
    Retrieve ESPN JSON data, either from cache or make new request.

    Args:
        url: ESPN API URL to fetch
        season: Season year
        cached_path: Base cache directory path (optional)

    Returns:
        dict: Parsed JSON data
    """
    data_type = get_data_type_from_url(url)
    data_type_id = get_data_type_id_from_url(url)
    league = get_league_from_url(url)
    return get_cached_url(url, league, season, data_type, data_type_id, cached_path)


def get_all(league, date_or_season_year, cached_path=None):
    """
    Fetch all ESPN data (schedule + games) for a league/season/date range.

    This is the main entry point for scraping. It:
    1. Gets schedule URLs for the requested league/date
    2. Fetches schedule data
    3. Extracts game IDs from schedule
    4. Fetches game, boxscore, and play-by-play data concurrently for each game

    Args:
        league: League identifier (e.g., "mens-college-basketball")
        date_or_season_year: Season year, date range, or single date
        cached_path: Base cache directory path (optional)

    Example:
        get_all("mens-college-basketball", "2024", "cached_data")
        get_all("womens-college-basketball", "20240315", "cached_data")
        get_all("mens-college-basketball", "20240101-20240331", "cached_data")
    """
    t1 = datetime.now()
    season = get_season(league, date_or_season_year)

    schedule_urls = get_schedule(league, date_or_season_year)

    t2 = datetime.now()
    logger.debug("Schedule Data elapsed time: %s", t2-t1)
    for url in schedule_urls:
        t3 = datetime.now()
        schedule = get_url(url, season, cached_path)
        date = get_data_type_id_from_url(url)
        game_ids = []
        if "error_msg" not in schedule:
            for event in schedule:
                if event["id"] not in game_ids:
                    game_ids.append(event["id"])
            logger.info("%s -> %d game_ids", date, len(game_ids))
        elif "error_msg" in schedule:
            logger.warning("SKIPPED schedule %s: %s - %s", url, schedule["error_code"], schedule["error_msg"])

        # Collect URLs that need fetching (not cached)
        urls_to_fetch = []
        url_metadata = []  # Track (url, data_type) for caching
        for game in game_ids:
            game_url = get_game_url(league, game)
            boxscore_url = get_boxscore_url(league, game)
            playbyplay_url = get_playbyplay_url(league, game)

            # Check cache for each URL
            for data_url, data_type in [
                (game_url, "game"),
                (boxscore_url, "boxscore"),
                (playbyplay_url, "playbyplay"),
            ]:
                if cached_path:
                    filename = get_filename(cached_path, league, season, data_type, data_url)
                    if is_cached(filename):
                        continue  # Skip cached files
                urls_to_fetch.append(data_url)
                url_metadata.append((data_url, data_type))

        # Fetch uncached URLs concurrently (3 at a time)
        if urls_to_fetch:
            logger.info("Fetching %d uncached URLs concurrently...", len(urls_to_fetch))
            results = get_multiple_json(urls_to_fetch, max_workers=3)

            # Process and cache results
            cached_count = 0
            skipped_count = 0
            for data_url, data_type in url_metadata:
                if data_url in results:
                    data = results[data_url]
                    if "error_msg" not in data:
                        data = data["page"]["content"]["gamepackage"]
                        cached_count += 1
                    else:
                        skipped_count += 1
                    if cached_path:
                        filename = get_filename(cached_path, league, season, data_type, data_url)
                        write_cache(filename, data)
            logger.info("Cached %d, skipped %d URLs", cached_count, skipped_count)

        t4 = datetime.now()
        logger.debug("Game Data elapsed time: %s", t4-t3)
    logger.info("Total elapsed time: %s", datetime.now()-t1)


def get_missing(league, date_or_season_year, cached_path="cached_data"):
    """
    Check cache for missing data and fetch it.

    This function:
    1. Gets schedule URLs for the requested league/date
    2. Checks if each schedule is cached
    3. For cached schedules, checks if all games are cached
    4. Fetches any missing data

    Args:
        league: League identifier
        date_or_season_year: Season year, date range, or single date
        cached_path: Base cache directory path (required)

    Raises:
        ValueError: If cached_path is not specified
    """
    if cached_path:
        season = get_season(league, date_or_season_year)
        schedule_urls = get_schedule(league, date_or_season_year)

        # Pre-create directories for game data types to avoid repeated os.makedirs checks
        for data_type in ["game", "boxscore", "playbyplay"]:
            dir_path = os.path.join(cached_path, league, season, data_type)
            os.makedirs(dir_path, exist_ok=True)

        # Store (url, data_type) tuples to avoid redundant URL parsing later
        missing_urls = []

        for url in schedule_urls:
            logger.debug("Checking: %s", url)
            data_type = get_data_type_from_url(url)
            data_type_id = get_data_type_id_from_url(url)
            filename = get_filename(cached_path, league, season, data_type, url)

            # If schedule date is cached, check if game, boxscore, and playbyplay are cached
            if is_cached(filename):
                schedule = get_cached_url(
                    url, league, season, data_type, data_type_id, cached_path
                )
                game_ids = set()  # Use set for O(1) lookups instead of list
                if "error_msg" not in schedule:
                    for event in schedule:
                        game_ids.add(event["id"])
                    logger.info("Cached: %s -> %d game_ids", filename, len(game_ids))
                elif "error_msg" in schedule:
                    logger.warning(
                        "Re-fetching cached error: %s - %s: %s",
                        schedule["error_code"], schedule["error_msg"], url
                    )

                    schedule = overwrite_cached_url(
                        url,
                        league,
                        season,
                        data_type,
                        data_type_id,
                        cached_path,
                        headers={"User-Agent": DEFAULT_USER_AGENT},
                    )

                    for event in schedule:
                        game_ids.add(event["id"])
                    logger.info("Re-fetched: %s -> %d game_ids", filename, len(game_ids))

                # Check cache for each game's data types
                # Generate URLs once and use os.path.isfile for fast existence check
                base_path = os.path.join(cached_path, league, season)
                for game in game_ids:
                    game_url = get_game_url(league, game)
                    boxscore_url = get_boxscore_url(league, game)
                    playbyplay_url = get_playbyplay_url(league, game)

                    # Build filenames directly (directories already exist)
                    game_file = f"{game}.json"
                    filename_game = os.path.join(base_path, "game", game_file)
                    filename_boxscore = os.path.join(base_path, "boxscore", game_file)
                    filename_playbyplay = os.path.join(base_path, "playbyplay", game_file)

                    # Use os.path.isfile for fast existence check (skip full JSON parse)
                    if not os.path.isfile(filename_game):
                        missing_urls.append((game_url, "game"))
                    if not os.path.isfile(filename_boxscore):
                        missing_urls.append((boxscore_url, "boxscore"))
                    if not os.path.isfile(filename_playbyplay):
                        missing_urls.append((playbyplay_url, "playbyplay"))

        logger.info("Search complete. Found %d URL(s) not cached.", len(missing_urls))

        if len(missing_urls) > 0:
            logger.info("Fetching %d missing URLs concurrently...", len(missing_urls))

            # Extract just URLs for fetching
            urls_to_fetch = [url for url, _ in missing_urls]

            # Fetch all missing URLs concurrently (3 at a time)
            results = get_multiple_json(urls_to_fetch, max_workers=3)

            # Process and cache results
            cached_count = 0
            skipped_count = 0
            for data_url, data_type in missing_urls:
                if data_url in results:
                    data = results[data_url]
                    if "error_msg" not in data:
                        if data_type in ["boxscore", "playbyplay", "game"]:
                            data = data["page"]["content"]["gamepackage"]
                        cached_count += 1
                    else:
                        skipped_count += 1
                    filename = get_filename(cached_path, league, season, data_type, data_url)
                    write_cache(filename, data)

            logger.info("Completed: cached %d, skipped %d", cached_count, skipped_count)
    else:
        raise ValueError("cached_path not specified.")
