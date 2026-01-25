"""
Orchestration module for ESPN parser.

This module provides high-level functions to parse all ESPN data
for a given league and season.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from espn_parser.leagues import validate_league, validate_season
from espn_parser.parsers import (
    parse_boxscore,
    parse_event,
    parse_game,
    parse_team_from_game,
    parse_team_from_schedule,
    parse_venue_from_schedule,
)
from espn_parser.parsers import (
    parse_playbyplay as parse_playbyplay_data,
)
from espn_parser.paths import DEFAULT_PARSED_BASE, DEFAULT_RAW_BASE
from espn_parser.reader import read_boxscores, read_games, read_playbyplay, read_schedules
from espn_parser.writer import (
    write_boxscores,
    write_events,
    write_games,
    write_playbyplay,
    write_players,
    write_teams,
    write_venues,
)


def parse_events(
    league: str,
    season: str,
    raw_path: Path | str | None = None,
    parsed_path: Path | str | None = None,
) -> dict[str, Path]:
    """
    Parse schedule events and related data (teams, venues) for a league and season.

    Args:
        league: League identifier
        season: Season year
        raw_path: Base path for raw data (default: data/raw/espn)
        parsed_path: Base path for parsed output (default: data/parsed/espn)

    Returns:
        Dictionary mapping output type to file path
    """
    validate_league(league)
    validate_season(league, season)

    raw_base = Path(raw_path) if raw_path else DEFAULT_RAW_BASE
    parsed_base = Path(parsed_path) if parsed_path else DEFAULT_PARSED_BASE

    events = []
    teams: dict[str, dict] = {}  # Deduplicate by id
    venues: dict[str, dict] = {}  # Deduplicate by id

    logger.info("Parsing schedule data for %s %s...", league, season)

    for date_str, schedule_events in read_schedules(league, season, raw_base):
        for event in schedule_events:
            # Parse event
            events.append(parse_event(event))

            # Parse teams from event (deduplicate)
            for team in event.get("teams", []):
                parsed = parse_team_from_schedule(team)
                teams[parsed["id"]] = parsed

            # Parse venue from event (deduplicate, keep first)
            venue = parse_venue_from_schedule(event)
            if venue and venue["id"] not in venues:
                venues[venue["id"]] = venue

    logger.info("  Found %d events, %d unique teams, %d unique venues", len(events), len(teams), len(venues))

    # Write outputs
    results = {}
    if events:
        path, count = write_events(events, league, season, parsed_base)
        results["events"] = path
        logger.info("  Wrote %d events to %s", count, path)
    if teams:
        path, count = write_teams(list(teams.values()), league, season, parsed_base)
        results["teams"] = path
        logger.info("  Wrote %d teams to %s", count, path)
    if venues:
        path, count = write_venues(list(venues.values()), league, season, parsed_base)
        results["venues"] = path
        logger.info("  Wrote %d venues to %s", count, path)

    return results


def parse_games(
    league: str,
    season: str,
    raw_path: Path | str | None = None,
    parsed_path: Path | str | None = None,
) -> dict[str, Path]:
    """
    Parse game data for a league and season.

    Args:
        league: League identifier
        season: Season year
        raw_path: Base path for raw data
        parsed_path: Base path for parsed output

    Returns:
        Dictionary mapping output type to file path
    """
    validate_league(league)
    validate_season(league, season)

    raw_base = Path(raw_path) if raw_path else DEFAULT_RAW_BASE
    parsed_base = Path(parsed_path) if parsed_path else DEFAULT_PARSED_BASE

    games = []
    teams: dict[str, dict] = {}  # Deduplicate by id

    logger.info("Parsing game data for %s %s...", league, season)

    for game_id, data in read_games(league, season, raw_base):
        # Parse game
        games.append(parse_game(game_id, data))

        # Parse teams from game (deduplicate, keep last)
        for team in data.get("gmStrp", {}).get("tms", []):
            parsed = parse_team_from_game(team)
            teams[parsed["id"]] = parsed

    logger.info("  Found %d games, %d unique teams", len(games), len(teams))

    # Write outputs
    results = {}
    if games:
        path, count = write_games(games, league, season, parsed_base)
        results["games"] = path
        logger.info("  Wrote %d games to %s", count, path)
    if teams:
        # Note: This will merge with teams from schedule if parse_all is used
        path, count = write_teams(list(teams.values()), league, season, parsed_base)
        results["teams"] = path
        logger.info("  Wrote %d teams to %s", count, path)

    return results


def parse_boxscores(
    league: str,
    season: str,
    raw_path: Path | str | None = None,
    parsed_path: Path | str | None = None,
) -> dict[str, Path]:
    """
    Parse boxscore data for a league and season.

    Args:
        league: League identifier
        season: Season year
        raw_path: Base path for raw data
        parsed_path: Base path for parsed output

    Returns:
        Dictionary mapping output type to file path
    """
    validate_league(league)
    validate_season(league, season)

    raw_base = Path(raw_path) if raw_path else DEFAULT_RAW_BASE
    parsed_base = Path(parsed_path) if parsed_path else DEFAULT_PARSED_BASE

    all_players = []
    all_boxscores = []

    logger.info("Parsing boxscore data for %s %s...", league, season)

    for game_id, data in read_boxscores(league, season, raw_base):
        players, boxscores = parse_boxscore(game_id, data)
        all_players.extend(players)
        all_boxscores.extend(boxscores)

    logger.info("  Found %d player records, %d boxscore records", len(all_players), len(all_boxscores))

    # Write outputs
    results = {}
    if all_players:
        path, count = write_players(all_players, league, season, parsed_base)
        results["players"] = path
        logger.info("  Wrote %d players to %s", count, path)
    if all_boxscores:
        path, count = write_boxscores(all_boxscores, league, season, parsed_base)
        results["boxscores"] = path
        logger.info("  Wrote %d boxscores to %s", count, path)

    return results


def parse_playbyplay(
    league: str,
    season: str,
    raw_path: Path | str | None = None,
    parsed_path: Path | str | None = None,
) -> dict[str, Path]:
    """
    Parse play-by-play data for a league and season.

    Args:
        league: League identifier
        season: Season year
        raw_path: Base path for raw data
        parsed_path: Base path for parsed output

    Returns:
        Dictionary mapping output type to file path
    """
    validate_league(league)
    validate_season(league, season)

    raw_base = Path(raw_path) if raw_path else DEFAULT_RAW_BASE
    parsed_base = Path(parsed_path) if parsed_path else DEFAULT_PARSED_BASE

    all_plays = []

    logger.info("Parsing play-by-play data for %s %s...", league, season)

    for game_id, data in read_playbyplay(league, season, raw_base):
        plays = parse_playbyplay_data(game_id, data)
        all_plays.extend(plays)

    logger.info("  Found %d play records", len(all_plays))

    # Write outputs
    results = {}
    if all_plays:
        path, count = write_playbyplay(all_plays, league, season, parsed_base)
        results["playbyplay"] = path
        logger.info("  Wrote %d plays to %s", count, path)

    return results


def parse_all(
    league: str,
    season: str,
    raw_path: Path | str | None = None,
    parsed_path: Path | str | None = None,
) -> dict[str, Path]:
    """
    Parse all ESPN data for a league and season.

    This function parses:
    - Events from schedule files
    - Games from game files
    - Teams from schedule and game files (merged and deduplicated)
    - Venues from schedule files
    - Players from boxscore files
    - Boxscores from boxscore files
    - Play-by-play from playbyplay files

    Args:
        league: League identifier
        season: Season year
        raw_path: Base path for raw data
        parsed_path: Base path for parsed output

    Returns:
        Dictionary mapping output type to file path
    """
    validate_league(league)
    validate_season(league, season)

    raw_base = Path(raw_path) if raw_path else DEFAULT_RAW_BASE
    parsed_base = Path(parsed_path) if parsed_path else DEFAULT_PARSED_BASE

    logger.info("Parsing all data for %s %s...", league, season)
    logger.info("=" * 60)

    # Collect all data
    events = []
    games = []
    teams: dict[str, dict] = {}  # Deduplicate by id during parsing
    venues: dict[str, dict] = {}  # Deduplicate by id during parsing
    players = []
    boxscores = []
    plays = []

    # 1. Parse schedules
    logger.info("[1/4] Parsing schedule files...")
    for date_str, schedule_events in read_schedules(league, season, raw_base):
        for event in schedule_events:
            events.append(parse_event(event))
            for team in event.get("teams", []):
                parsed = parse_team_from_schedule(team)
                teams[parsed["id"]] = parsed  # Will be overwritten by game data
            venue = parse_venue_from_schedule(event)
            if venue:
                if venue["id"] not in venues:  # Keep first occurrence
                    venues[venue["id"]] = venue
    logger.info("  -> %d events, %d unique venues", len(events), len(venues))

    # 2. Parse games
    logger.info("[2/4] Parsing game files...")
    for game_id, data in read_games(league, season, raw_base):
        games.append(parse_game(game_id, data))
        for team in data.get("gmStrp", {}).get("tms", []):
            parsed = parse_team_from_game(team)
            teams[parsed["id"]] = parsed  # Overwrites schedule data (has conference)
    logger.info("  -> %d games, %d unique teams", len(games), len(teams))

    # 3. Parse boxscores
    logger.info("[3/4] Parsing boxscore files...")
    for game_id, data in read_boxscores(league, season, raw_base):
        game_players, game_boxscores = parse_boxscore(game_id, data)
        players.extend(game_players)
        boxscores.extend(game_boxscores)
    logger.info("  -> %d boxscore records, %d player records", len(boxscores), len(players))

    # 4. Parse play-by-play
    logger.info("[4/4] Parsing play-by-play files...")
    for game_id, data in read_playbyplay(league, season, raw_base):
        game_plays = parse_playbyplay_data(game_id, data)
        plays.extend(game_plays)
    logger.info("  -> %d play records", len(plays))

    # Write all outputs
    logger.info("=" * 60)
    logger.info("Writing parquet files...")

    results = {}

    if events:
        path, count = write_events(events, league, season, parsed_base)
        results["events"] = path
        logger.info("  events.parquet: %d records", count)

    if games:
        path, count = write_games(games, league, season, parsed_base)
        results["games"] = path
        logger.info("  games.parquet: %d records", count)

    if teams:
        path, count = write_teams(list(teams.values()), league, season, parsed_base)
        results["teams"] = path
        logger.info("  teams.parquet: %d unique teams", count)

    if venues:
        path, count = write_venues(list(venues.values()), league, season, parsed_base)
        results["venues"] = path
        logger.info("  venues.parquet: %d unique venues", count)

    if players:
        path, count = write_players(players, league, season, parsed_base)
        results["players"] = path
        logger.info("  players.parquet: %d unique players", count)

    if boxscores:
        path, count = write_boxscores(boxscores, league, season, parsed_base)
        results["boxscores"] = path
        logger.info("  boxscores.parquet: %d records", count)

    if plays:
        path, count = write_playbyplay(plays, league, season, parsed_base)
        results["playbyplay"] = path
        logger.info("  playbyplay.parquet: %d records", count)

    logger.info("=" * 60)
    logger.info("Done! Output directory: %s", parsed_base / league / season)

    return results
