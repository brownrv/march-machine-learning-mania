"""
Orchestration module for ESPN parser.

This module provides high-level functions to parse all ESPN data
for a given league and season.
"""

from pathlib import Path

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
    teams = []
    venues = []

    print(f"Parsing schedule data for {league} {season}...")

    for date_str, schedule_events in read_schedules(league, season, raw_base):
        for event in schedule_events:
            # Parse event
            events.append(parse_event(event))

            # Parse teams from event
            event_teams = event.get("teams", [])
            for team in event_teams:
                teams.append(parse_team_from_schedule(team))

            # Parse venue from event
            venue = parse_venue_from_schedule(event)
            if venue:
                venues.append(venue)

    print(f"  Found {len(events)} events, {len(teams)} team records, {len(venues)} venue records")

    # Write outputs
    results = {}
    if events:
        results["events"] = write_events(events, league, season, parsed_base)
        print(f"  Wrote events to {results['events']}")
    if teams:
        results["teams"] = write_teams(teams, league, season, parsed_base)
        print(f"  Wrote teams to {results['teams']}")
    if venues:
        results["venues"] = write_venues(venues, league, season, parsed_base)
        print(f"  Wrote venues to {results['venues']}")

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
    teams = []

    print(f"Parsing game data for {league} {season}...")

    for game_id, data in read_games(league, season, raw_base):
        # Parse game
        games.append(parse_game(game_id, data))

        # Parse teams from game
        gm_strp = data.get("gmStrp", {})
        for team in gm_strp.get("tms", []):
            teams.append(parse_team_from_game(team))

    print(f"  Found {len(games)} games, {len(teams)} team records")

    # Write outputs
    results = {}
    if games:
        results["games"] = write_games(games, league, season, parsed_base)
        print(f"  Wrote games to {results['games']}")
    if teams:
        # Note: This will merge with teams from schedule if parse_all is used
        results["teams"] = write_teams(teams, league, season, parsed_base)
        print(f"  Wrote teams to {results['teams']}")

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

    print(f"Parsing boxscore data for {league} {season}...")

    for game_id, data in read_boxscores(league, season, raw_base):
        players, boxscores = parse_boxscore(game_id, data)
        all_players.extend(players)
        all_boxscores.extend(boxscores)

    print(f"  Found {len(all_players)} player records, {len(all_boxscores)} boxscore records")

    # Write outputs
    results = {}
    if all_players:
        results["players"] = write_players(all_players, league, season, parsed_base)
        print(f"  Wrote players to {results['players']}")
    if all_boxscores:
        results["boxscores"] = write_boxscores(all_boxscores, league, season, parsed_base)
        print(f"  Wrote boxscores to {results['boxscores']}")

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

    print(f"Parsing play-by-play data for {league} {season}...")

    for game_id, data in read_playbyplay(league, season, raw_base):
        plays = parse_playbyplay_data(game_id, data)
        all_plays.extend(plays)

    print(f"  Found {len(all_plays)} play records")

    # Write outputs
    results = {}
    if all_plays:
        results["playbyplay"] = write_playbyplay(all_plays, league, season, parsed_base)
        print(f"  Wrote playbyplay to {results['playbyplay']}")

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

    print(f"Parsing all data for {league} {season}...")
    print("=" * 60)

    # Collect all data
    events = []
    games = []
    teams = []
    venues = []
    players = []
    boxscores = []
    plays = []

    # 1. Parse schedules
    print("\n[1/4] Parsing schedule files...")
    for date_str, schedule_events in read_schedules(league, season, raw_base):
        for event in schedule_events:
            events.append(parse_event(event))
            for team in event.get("teams", []):
                teams.append(parse_team_from_schedule(team))
            venue = parse_venue_from_schedule(event)
            if venue:
                venues.append(venue)
    print(f"  -> {len(events)} events, {len(venues)} venues")

    # 2. Parse games
    print("\n[2/4] Parsing game files...")
    for game_id, data in read_games(league, season, raw_base):
        games.append(parse_game(game_id, data))
        gm_strp = data.get("gmStrp", {})
        for team in gm_strp.get("tms", []):
            teams.append(parse_team_from_game(team))
    print(f"  -> {len(games)} games")

    # 3. Parse boxscores
    print("\n[3/4] Parsing boxscore files...")
    for game_id, data in read_boxscores(league, season, raw_base):
        game_players, game_boxscores = parse_boxscore(game_id, data)
        players.extend(game_players)
        boxscores.extend(game_boxscores)
    print(f"  -> {len(boxscores)} boxscore records, {len(players)} player records")

    # 4. Parse play-by-play
    print("\n[4/4] Parsing play-by-play files...")
    for game_id, data in read_playbyplay(league, season, raw_base):
        game_plays = parse_playbyplay_data(game_id, data)
        plays.extend(game_plays)
    print(f"  -> {len(plays)} play records")

    # Write all outputs
    print("\n" + "=" * 60)
    print("Writing parquet files...")

    results = {}

    if events:
        results["events"] = write_events(events, league, season, parsed_base)
        print(f"  events.parquet: {len(events)} records")

    if games:
        results["games"] = write_games(games, league, season, parsed_base)
        print(f"  games.parquet: {len(games)} records")

    if teams:
        results["teams"] = write_teams(teams, league, season, parsed_base)
        # Count deduplicated teams
        import pandas as pd

        teams_df = pd.read_parquet(results["teams"])
        print(f"  teams.parquet: {len(teams_df)} unique teams")

    if venues:
        results["venues"] = write_venues(venues, league, season, parsed_base)
        import pandas as pd

        venues_df = pd.read_parquet(results["venues"])
        print(f"  venues.parquet: {len(venues_df)} unique venues")

    if players:
        results["players"] = write_players(players, league, season, parsed_base)
        import pandas as pd

        players_df = pd.read_parquet(results["players"])
        print(f"  players.parquet: {len(players_df)} unique players")

    if boxscores:
        results["boxscores"] = write_boxscores(boxscores, league, season, parsed_base)
        print(f"  boxscores.parquet: {len(boxscores)} records")

    if plays:
        results["playbyplay"] = write_playbyplay(plays, league, season, parsed_base)
        print(f"  playbyplay.parquet: {len(plays)} records")

    print("\n" + "=" * 60)
    print(f"Done! Output directory: {parsed_base / league / season}")

    return results
