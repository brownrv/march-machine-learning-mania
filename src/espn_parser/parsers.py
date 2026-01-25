"""
Parsing transformations for ESPN data.

This module contains functions to transform raw ESPN JSON data into
structured dictionaries ready for DataFrame conversion.
"""

from typing import Any


def safe_get(data: dict | None, *keys: str, default: Any = None) -> Any:
    """
    Safely navigate nested dictionaries.

    Args:
        data: The dictionary to navigate
        *keys: Keys to traverse
        default: Default value if path doesn't exist

    Returns:
        The value at the path, or default if not found
    """
    if data is None:
        return default
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def safe_int(value: Any, default: int | None = None) -> int | None:
    """Convert a value to int, returning default if conversion fails."""
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float | None = None) -> float | None:
    """Convert a value to float, returning default if conversion fails."""
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_made_attempted(value: str | None) -> tuple[int | None, int | None]:
    """
    Parse a 'made-attempted' string like '8-11' into (made, attempted).

    Args:
        value: String in format 'made-attempted' (e.g., '8-11')

    Returns:
        Tuple of (made, attempted) as integers, or (None, None) if invalid
    """
    if not value or not isinstance(value, str):
        return None, None
    parts = value.split("-")
    if len(parts) != 2:
        return None, None
    return safe_int(parts[0]), safe_int(parts[1])


def parse_event(event: dict[str, Any]) -> dict[str, Any]:
    """
    Parse a schedule event into structured format.

    Args:
        event: Raw event dictionary from schedule JSON

    Returns:
        Parsed event dictionary
    """
    return {
        "id": str(event.get("id", "")),
        "date": event.get("date", ""),
        "link": event.get("link", ""),
        "completed": event.get("completed", False),
        "neutralSite": event.get("neutralSite", False),
    }


def parse_team_from_schedule(team: dict[str, Any]) -> dict[str, Any]:
    """
    Parse team data from schedule event.

    Args:
        team: Team dictionary from schedule event

    Returns:
        Parsed team dictionary
    """
    return {
        "id": str(team.get("id", "")),
        "abbrev": team.get("abbrev", ""),
        "displayName": team.get("displayName", ""),
        "location": team.get("location", ""),
        "shortDisplayName": team.get("shortDisplayName", ""),
        "links": team.get("links", ""),
        "logo": team.get("logo", ""),
        "color": team.get("teamColor", ""),
        "altColor": team.get("altColor", ""),
        "conferenceId": str(team.get("conferenceId", "")) if team.get("conferenceId") else None,
        "conference": None,  # Not available in schedule
    }


def parse_team_from_game(team: dict[str, Any]) -> dict[str, Any]:
    """
    Parse team data from game file.

    Args:
        team: Team dictionary from gmStrp.tms[]

    Returns:
        Parsed team dictionary
    """
    return {
        "id": str(team.get("id", "")),
        "abbrev": team.get("abbrev", ""),
        "displayName": team.get("displayName", ""),
        "location": team.get("location", ""),
        "shortDisplayName": team.get("shortDisplayName", ""),
        "links": team.get("links", ""),
        "logo": team.get("logo", ""),
        "color": team.get("teamColor", ""),
        "altColor": team.get("altColor", ""),
        "conferenceId": None,  # Not typically in game file
        "conference": team.get("conference", ""),
    }


def parse_venue_from_schedule(event: dict[str, Any]) -> dict[str, Any] | None:
    """
    Parse venue data from schedule event.

    Args:
        event: Event dictionary from schedule

    Returns:
        Parsed venue dictionary, or None if no venue data
    """
    venue = event.get("venue")
    if not venue:
        return None

    address = venue.get("address", {})
    return {
        "id": str(venue.get("id", "")),
        "fullName": venue.get("fullName", ""),
        "capacity": safe_int(venue.get("capacity")),
        "city": address.get("city", ""),
        "state": address.get("state", ""),
    }


def parse_game(game_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Parse game data from game file.

    Args:
        game_id: The game ID
        data: Raw game data dictionary

    Returns:
        Parsed game dictionary
    """
    gm_info = data.get("gmInfo", {})
    gm_strp = data.get("gmStrp", {})
    gm_stry = data.get("gmStry", {})
    teams = gm_strp.get("tms", [{}, {}])

    # Ensure we have two teams
    tm1 = teams[0] if len(teams) > 0 else {}
    tm2 = teams[1] if len(teams) > 1 else {}

    # Parse referees
    refs = gm_info.get("refs", [])
    ref1 = refs[0].get("dspNm") if len(refs) > 0 and isinstance(refs[0], dict) else None
    ref2 = refs[1].get("dspNm") if len(refs) > 1 and isinstance(refs[1], dict) else None
    ref3 = refs[2].get("dspNm") if len(refs) > 2 and isinstance(refs[2], dict) else None

    # Determine if conference game (compare team conferences if available)
    tm1_conf = tm1.get("conference", "")
    tm2_conf = tm2.get("conference", "")
    is_conference_game = None
    if tm1_conf and tm2_conf:
        is_conference_game = tm1_conf == tm2_conf

    return {
        "gid": str(game_id),
        "dtTm": gm_info.get("dtTm", ""),
        "gameState": gm_info.get("gameState", ""),
        "attnd": safe_int(gm_info.get("attnd")),
        "cpcty": safe_int(gm_info.get("cpcty")),
        "lne": safe_float(gm_info.get("lne")),
        "ovUnd": safe_float(gm_info.get("ovUnd")),
        "loc": gm_info.get("loc", ""),
        "locImg": str(gm_info.get("locImg", "")) if gm_info.get("locImg") else None,
        "venueId": str(gm_info.get("venueId", "")) if gm_info.get("venueId") else None,
        "ref1": ref1,
        "ref2": ref2,
        "ref3": ref3,
        "isConferenceGame": is_conference_game,
        # Team 1
        "tm1_id": str(tm1.get("id", "")),
        "tm1_displayName": tm1.get("displayName", ""),
        "tm1_abbrev": tm1.get("abbrev", ""),
        "tm1_isHome": tm1.get("isHome", False),
        "tm1_logo": tm1.get("logo", ""),
        "tm1_logoDk": tm1.get("logoDk", ""),
        "tm1_logoMd": tm1.get("logoMd", ""),
        "tm1_rank": safe_int(tm1.get("rank")),
        "tm1_score": safe_int(tm1.get("score")),
        "tm1_winner": tm1.get("winner", False),
        "tm1_conference": tm1.get("conference", ""),
        "tm1_recordTotal": tm1.get("recordTotal", ""),
        # Team 2
        "tm2_id": str(tm2.get("id", "")),
        "tm2_displayName": tm2.get("displayName", ""),
        "tm2_abbrev": tm2.get("abbrev", ""),
        "tm2_isHome": tm2.get("isHome", False),
        "tm2_logo": tm2.get("logo", ""),
        "tm2_logoDk": tm2.get("logoDk", ""),
        "tm2_logoMd": tm2.get("logoMd", ""),
        "tm2_rank": safe_int(tm2.get("rank")),
        "tm2_score": safe_int(tm2.get("score")),
        "tm2_winner": tm2.get("winner", False),
        "tm2_conference": tm2.get("conference", ""),
        "tm2_recordTotal": tm2.get("recordTotal", ""),
        # Story
        "hdln": gm_stry.get("hdln"),
        "desc": gm_stry.get("desc"),
    }


def parse_player_from_boxscore(
    team_id: str,
    team_name: str,
    athlete: dict[str, Any],
) -> dict[str, Any]:
    """
    Parse player data from boxscore athlete entry.

    Args:
        team_id: The team ID
        team_name: The team display name
        athlete: Athlete dictionary from boxscore

    Returns:
        Parsed player dictionary
    """
    athlt = athlete.get("athlt", {})
    return {
        "aid": str(athlt.get("id", "")),
        "athleteName": athlt.get("dspNm", ""),
        "tid": str(team_id),
        "teamName": team_name,
        "pos": athlt.get("pos", ""),
        "lnk": athlt.get("lnk", ""),
        "jersey": athlt.get("jersey"),
    }


def parse_boxscore_stats(
    game_id: str,
    team_id: str,
    team_name: str,
    athlete: dict[str, Any],
    starter_bench: str,
) -> dict[str, Any]:
    """
    Parse boxscore statistics for a player.

    Args:
        game_id: The game ID
        team_id: The team ID
        team_name: The team display name
        athlete: Athlete dictionary from boxscore
        starter_bench: Either "starters", "bench", or "totals"

    Returns:
        Parsed boxscore dictionary
    """
    athlt = athlete.get("athlt", {})
    stats = athlete.get("stats", [])

    # Stats array indices (based on lbls order):
    # 0: MIN, 1: PTS, 2: FG, 3: 3PT, 4: FT, 5: REB, 6: AST, 7: TO,
    # 8: STL, 9: BLK, 10: OREB, 11: DREB, 12: PF

    def get_stat(idx: int) -> str | None:
        return stats[idx] if len(stats) > idx else None

    fg_made, fg_att = parse_made_attempted(get_stat(2))
    three_made, three_att = parse_made_attempted(get_stat(3))
    ft_made, ft_att = parse_made_attempted(get_stat(4))

    return {
        "gid": str(game_id),
        "tid": str(team_id),
        "teamName": team_name,
        "aid": str(athlt.get("id", "")),
        "athleteName": athlt.get("dspNm", ""),
        "starterBench": starter_bench,
        "MIN": safe_int(get_stat(0)),
        "FG_made": fg_made,
        "FG_att": fg_att,
        "3PT_made": three_made,
        "3PT_att": three_att,
        "FT_made": ft_made,
        "FT_att": ft_att,
        "OREB": safe_int(get_stat(10)),
        "DREB": safe_int(get_stat(11)),
        "REB": safe_int(get_stat(5)),
        "AST": safe_int(get_stat(6)),
        "STL": safe_int(get_stat(8)),
        "BLK": safe_int(get_stat(9)),
        "TO": safe_int(get_stat(7)),
        "PF": safe_int(get_stat(12)),
        "PTS": safe_int(get_stat(1)),
    }


def parse_boxscore(
    game_id: str, data: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Parse boxscore data into player records and boxscore stats.

    Args:
        game_id: The game ID
        data: Raw boxscore data dictionary

    Returns:
        Tuple of (players_list, boxscores_list)
    """
    players = []
    boxscores = []
    seen_players = set()

    bxscr = data.get("bxscr", [])
    for team_data in bxscr:
        team = team_data.get("tm", {})
        team_id = team.get("id", "")
        team_name = team.get("dspNm", "")

        stats_groups = team_data.get("stats", [])
        for stats_group in stats_groups:
            group_type = stats_group.get("type", "")
            # Skip totals for individual player stats
            if group_type == "totals":
                continue

            athletes = stats_group.get("athlts", [])
            for athlete in athletes:
                athlt = athlete.get("athlt", {})
                aid = athlt.get("id", "")

                # Add player (deduplicate by aid)
                if aid and aid not in seen_players:
                    players.append(parse_player_from_boxscore(team_id, team_name, athlete))
                    seen_players.add(aid)

                # Add boxscore stats
                if aid:
                    boxscores.append(
                        parse_boxscore_stats(game_id, team_id, team_name, athlete, group_type)
                    )

    return players, boxscores


def parse_play(game_id: str, play: dict[str, Any]) -> dict[str, Any]:
    """
    Parse a single play-by-play event.

    Args:
        game_id: The game ID
        play: Raw play dictionary

    Returns:
        Parsed play dictionary
    """
    period = play.get("period", {})
    clock = play.get("clock", {})

    return {
        "gid": str(game_id),
        "id": str(play.get("id", "")),
        "period": safe_int(period.get("number"), 0),
        "periodDisplayValue": period.get("displayValue", ""),
        "time": clock.get("displayValue", ""),
        "awayScore": safe_int(play.get("awayScore"), 0),
        "homeScore": safe_int(play.get("homeScore"), 0),
        "homeAway": play.get("homeAway", ""),
        "description": play.get("text", ""),
        "scoringPlay": play.get("scoringPlay", False),
    }


def parse_playbyplay(game_id: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Parse play-by-play data for a game.

    Args:
        game_id: The game ID
        data: Raw playbyplay data dictionary

    Returns:
        List of parsed play dictionaries
    """
    plays = []
    pbp = data.get("pbp", {})
    play_grps = pbp.get("playGrps", [])

    for period_plays in play_grps:
        if not isinstance(period_plays, list):
            continue
        for play in period_plays:
            if isinstance(play, dict):
                plays.append(parse_play(game_id, play))

    return plays
