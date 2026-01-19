"""
Data models and type definitions for ESPN parser.

This module defines TypedDicts for the structured output data.
These serve as documentation and type hints for the parsed data.
"""

from typing import TypedDict


class Event(TypedDict, total=False):
    """Schedule event from schedule files."""

    id: str
    date: str
    link: str
    completed: bool
    neutralSite: bool


class Game(TypedDict, total=False):
    """Game data from game files."""

    gid: str
    dtTm: str
    gameState: str
    attnd: int | None
    cpcty: int | None
    lne: float | None
    ovUnd: float | None
    loc: str
    locImg: str | None  # Can be "True", "False", or venue image URL
    venueId: str | None
    ref1: str | None
    ref2: str | None
    ref3: str | None
    isConferenceGame: bool | None
    # Team 1
    tm1_id: str
    tm1_displayName: str
    tm1_abbrev: str
    tm1_isHome: bool
    tm1_logo: str
    tm1_logoDk: str
    tm1_logoMd: str
    tm1_rank: int | None
    tm1_score: str
    tm1_winner: bool
    tm1_conference: str
    tm1_recordTotal: str
    # Team 2
    tm2_id: str
    tm2_displayName: str
    tm2_abbrev: str
    tm2_isHome: bool
    tm2_logo: str
    tm2_logoDk: str
    tm2_logoMd: str
    tm2_rank: int | None
    tm2_score: str
    tm2_winner: bool
    tm2_conference: str
    tm2_recordTotal: str
    # Story
    hdln: str | None
    desc: str | None


class Team(TypedDict, total=False):
    """Team data extracted from various sources."""

    id: str
    abbrev: str
    displayName: str
    location: str
    shortDisplayName: str
    links: str
    logo: str
    color: str
    altColor: str
    conferenceId: str | None
    conference: str | None


class Venue(TypedDict, total=False):
    """Venue data extracted from schedule/game files."""

    id: str
    fullName: str
    capacity: int | None
    city: str
    state: str


class Player(TypedDict, total=False):
    """Player data extracted from boxscore files."""

    aid: str
    athleteName: str
    tid: str
    teamName: str
    pos: str
    lnk: str
    jersey: str | None


class BoxScore(TypedDict, total=False):
    """Player box score statistics from boxscore files."""

    gid: str
    tid: str
    teamName: str
    aid: str
    athleteName: str
    starterBench: str
    MIN: int | None
    FG_made: int | None
    FG_att: int | None
    threePT_made: int | None  # 3PT_made (renamed for Python compatibility)
    threePT_att: int | None  # 3PT_att
    FT_made: int | None
    FT_att: int | None
    OREB: int | None
    DREB: int | None
    REB: int | None
    AST: int | None
    STL: int | None
    BLK: int | None
    TO: int | None
    PF: int | None
    PTS: int | None


class Play(TypedDict, total=False):
    """Play-by-play event from playbyplay files."""

    gid: str
    id: str
    period: int
    periodDisplayValue: str
    time: str
    awayScore: int
    homeScore: int
    homeAway: str
    description: str
    scoringPlay: bool


# Column name mappings for parquet output
# These map internal names to the final column names in parquet files

BOXSCORE_COLUMNS = [
    "gid",
    "tid",
    "teamName",
    "aid",
    "athleteName",
    "starterBench",
    "MIN",
    "FG_made",
    "FG_att",
    "3PT_made",
    "3PT_att",
    "FT_made",
    "FT_att",
    "OREB",
    "DREB",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TO",
    "PF",
    "PTS",
]

GAME_COLUMNS = [
    "gid",
    "dtTm",
    "gameState",
    "attnd",
    "cpcty",
    "lne",
    "ovUnd",
    "loc",
    "locImg",
    "venueId",
    "ref1",
    "ref2",
    "ref3",
    "isConferenceGame",
    "tm1_id",
    "tm1_displayName",
    "tm1_abbrev",
    "tm1_isHome",
    "tm1_logo",
    "tm1_logoDk",
    "tm1_logoMd",
    "tm1_rank",
    "tm1_score",
    "tm1_winner",
    "tm1_conference",
    "tm1_recordTotal",
    "tm2_id",
    "tm2_displayName",
    "tm2_abbrev",
    "tm2_isHome",
    "tm2_logo",
    "tm2_logoDk",
    "tm2_logoMd",
    "tm2_rank",
    "tm2_score",
    "tm2_winner",
    "tm2_conference",
    "tm2_recordTotal",
    "hdln",
    "desc",
]

EVENT_COLUMNS = ["id", "date", "link", "completed", "neutralSite"]

TEAM_COLUMNS = [
    "id",
    "abbrev",
    "displayName",
    "location",
    "shortDisplayName",
    "links",
    "logo",
    "color",
    "altColor",
    "conferenceId",
    "conference",
]

VENUE_COLUMNS = ["id", "fullName", "capacity", "city", "state"]

PLAYER_COLUMNS = ["aid", "athleteName", "tid", "teamName", "pos", "lnk", "jersey"]

PLAY_COLUMNS = [
    "gid",
    "id",
    "period",
    "periodDisplayValue",
    "time",
    "awayScore",
    "homeScore",
    "homeAway",
    "description",
    "scoringPlay",
]
