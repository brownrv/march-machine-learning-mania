"""Tests for espn_parser.parsers module."""

import pytest

from espn_parser.parsers import (
    parse_boxscore,
    parse_boxscore_stats,
    parse_event,
    parse_game,
    parse_made_attempted,
    parse_play,
    parse_player_from_boxscore,
    parse_playbyplay,
    parse_team_from_game,
    parse_team_from_schedule,
    parse_venue_from_schedule,
    safe_float,
    safe_get,
    safe_int,
)


class TestSafeGet:
    """Tests for safe_get function."""

    def test_simple_key(self):
        """Test getting a simple key."""
        data = {"a": 1}
        assert safe_get(data, "a") == 1

    def test_nested_keys(self):
        """Test getting nested keys."""
        data = {"a": {"b": {"c": 3}}}
        assert safe_get(data, "a", "b", "c") == 3

    def test_missing_key_returns_default(self):
        """Test that missing key returns default."""
        data = {"a": 1}
        assert safe_get(data, "b") is None
        assert safe_get(data, "b", default="default") == "default"

    def test_none_data_returns_default(self):
        """Test that None data returns default."""
        assert safe_get(None, "a") is None

    def test_intermediate_missing_key(self):
        """Test missing intermediate key."""
        data = {"a": {"b": 2}}
        assert safe_get(data, "a", "c", "d") is None


class TestSafeInt:
    """Tests for safe_int function."""

    def test_valid_int(self):
        """Test converting valid integer."""
        assert safe_int(42) == 42

    def test_string_int(self):
        """Test converting string integer."""
        assert safe_int("42") == 42

    def test_none_returns_default(self):
        """Test that None returns default."""
        assert safe_int(None) is None
        assert safe_int(None, default=0) == 0

    def test_empty_string_returns_default(self):
        """Test that empty string returns default."""
        assert safe_int("") is None

    def test_invalid_returns_default(self):
        """Test that invalid value returns default."""
        assert safe_int("not a number") is None


class TestSafeFloat:
    """Tests for safe_float function."""

    def test_valid_float(self):
        """Test converting valid float."""
        assert safe_float(3.14) == 3.14

    def test_string_float(self):
        """Test converting string float."""
        assert safe_float("3.14") == 3.14

    def test_none_returns_default(self):
        """Test that None returns default."""
        assert safe_float(None) is None

    def test_invalid_returns_default(self):
        """Test that invalid value returns default."""
        assert safe_float("not a number") is None


class TestParseMadeAttempted:
    """Tests for parse_made_attempted function."""

    def test_valid_format(self):
        """Test parsing valid made-attempted format."""
        made, attempted = parse_made_attempted("8-11")
        assert made == 8
        assert attempted == 11

    def test_zeros(self):
        """Test parsing zeros."""
        made, attempted = parse_made_attempted("0-0")
        assert made == 0
        assert attempted == 0

    def test_none_returns_nones(self):
        """Test that None returns (None, None)."""
        made, attempted = parse_made_attempted(None)
        assert made is None
        assert attempted is None

    def test_empty_string_returns_nones(self):
        """Test that empty string returns (None, None)."""
        made, attempted = parse_made_attempted("")
        assert made is None
        assert attempted is None

    def test_invalid_format_returns_nones(self):
        """Test that invalid format returns (None, None)."""
        made, attempted = parse_made_attempted("invalid")
        assert made is None
        assert attempted is None


class TestParseEvent:
    """Tests for parse_event function."""

    def test_parses_all_fields(self):
        """Test parsing all event fields."""
        event = {
            "id": "401573353",
            "date": "2024-03-01T02:00Z",
            "link": "/game/401573353",
            "completed": True,
            "neutralSite": False,
        }
        result = parse_event(event)

        assert result["id"] == "401573353"
        assert result["date"] == "2024-03-01T02:00Z"
        assert result["link"] == "/game/401573353"
        assert result["completed"] is True
        assert result["neutralSite"] is False

    def test_handles_missing_fields(self):
        """Test handling missing fields with defaults."""
        event = {"id": "123"}
        result = parse_event(event)

        assert result["id"] == "123"
        assert result["date"] == ""
        assert result["completed"] is False
        assert result["neutralSite"] is False


class TestParseTeamFromSchedule:
    """Tests for parse_team_from_schedule function."""

    def test_parses_all_fields(self):
        """Test parsing all team fields from schedule."""
        team = {
            "id": "2305",
            "abbrev": "KU",
            "displayName": "Kansas Jayhawks",
            "location": "Kansas",
            "shortDisplayName": "Jayhawks",
            "links": "/team/2305",
            "logo": "https://example.com/logo.png",
            "teamColor": "0051BA",
            "altColor": "E8000D",
            "conferenceId": "8",
        }
        result = parse_team_from_schedule(team)

        assert result["id"] == "2305"
        assert result["abbrev"] == "KU"
        assert result["displayName"] == "Kansas Jayhawks"
        assert result["color"] == "0051BA"
        assert result["conferenceId"] == "8"
        assert result["conference"] is None  # Not in schedule

    def test_handles_missing_conference_id(self):
        """Test handling missing conference ID."""
        team = {"id": "123"}
        result = parse_team_from_schedule(team)
        assert result["conferenceId"] is None


class TestParseTeamFromGame:
    """Tests for parse_team_from_game function."""

    def test_parses_conference_field(self):
        """Test that conference field is parsed from game."""
        team = {
            "id": "149",
            "displayName": "Montana Grizzlies",
            "conference": "Big Sky",
        }
        result = parse_team_from_game(team)

        assert result["id"] == "149"
        assert result["conference"] == "Big Sky"
        assert result["conferenceId"] is None  # Not in game


class TestParseVenueFromSchedule:
    """Tests for parse_venue_from_schedule function."""

    def test_parses_venue(self):
        """Test parsing venue from schedule event."""
        event = {
            "venue": {
                "id": "2171",
                "fullName": "Allen Fieldhouse",
                "capacity": 16300,
                "address": {"city": "Lawrence", "state": "KS"},
            }
        }
        result = parse_venue_from_schedule(event)

        assert result["id"] == "2171"
        assert result["fullName"] == "Allen Fieldhouse"
        assert result["capacity"] == 16300
        assert result["city"] == "Lawrence"
        assert result["state"] == "KS"

    def test_no_venue_returns_none(self):
        """Test that missing venue returns None."""
        event = {}
        result = parse_venue_from_schedule(event)
        assert result is None


class TestParseGame:
    """Tests for parse_game function."""

    def test_parses_basic_game(self):
        """Test parsing basic game data."""
        data = {
            "gmInfo": {
                "dtTm": "2024-03-01T02:00Z",
                "gameState": "post",
                "attnd": 2179,
                "loc": "Reese Court",
                "refs": [
                    {"dspNm": "Ryan Holmes"},
                    {"dspNm": "Jimmy Casas"},
                    {"dspNm": "Peter Larson"},
                ],
            },
            "gmStrp": {
                "gid": "401573353",
                "tms": [
                    {
                        "id": "149",
                        "displayName": "Montana Grizzlies",
                        "abbrev": "MONT",
                        "isHome": False,
                        "score": "79",
                        "winner": False,
                        "conference": "Big Sky",
                    },
                    {
                        "id": "331",
                        "displayName": "Eastern Washington Eagles",
                        "abbrev": "EWU",
                        "isHome": True,
                        "score": "89",
                        "winner": True,
                        "conference": "Big Sky",
                    },
                ],
            },
            "gmStry": {
                "hdln": "Jones scores 30",
                "desc": "Casey Jones led the way...",
            },
        }

        result = parse_game("401573353", data)

        assert result["gid"] == "401573353"
        assert result["dtTm"] == "2024-03-01T02:00Z"
        assert result["gameState"] == "post"
        assert result["attnd"] == 2179
        assert result["ref1"] == "Ryan Holmes"
        assert result["ref2"] == "Jimmy Casas"
        assert result["ref3"] == "Peter Larson"
        assert result["tm1_id"] == "149"
        assert result["tm1_displayName"] == "Montana Grizzlies"
        assert result["tm1_score"] == 79
        assert result["tm2_score"] == 89
        assert result["tm2_winner"] is True
        assert result["isConferenceGame"] is True  # Same conference

    def test_conference_game_detection(self):
        """Test conference game detection."""
        # Different conferences
        data = {
            "gmInfo": {},
            "gmStrp": {
                "tms": [
                    {"id": "1", "conference": "Big Sky"},
                    {"id": "2", "conference": "Big Ten"},
                ]
            },
        }
        result = parse_game("123", data)
        assert result["isConferenceGame"] is False


class TestParsePlayerFromBoxscore:
    """Tests for parse_player_from_boxscore function."""

    def test_parses_player(self):
        """Test parsing player from boxscore."""
        athlete = {
            "athlt": {
                "id": "5107840",
                "dspNm": "Laolu Oke",
                "pos": "F",
                "lnk": "https://espn.com/player/5107840",
                "jersey": "22",
            }
        }
        result = parse_player_from_boxscore("149", "Montana Grizzlies", athlete)

        assert result["aid"] == "5107840"
        assert result["athleteName"] == "Laolu Oke"
        assert result["tid"] == "149"
        assert result["teamName"] == "Montana Grizzlies"
        assert result["pos"] == "F"
        assert result["jersey"] == "22"


class TestParseBoxscoreStats:
    """Tests for parse_boxscore_stats function."""

    def test_parses_stats(self):
        """Test parsing boxscore statistics."""
        athlete = {
            "athlt": {"id": "5107840", "dspNm": "Laolu Oke"},
            "stats": ["27", "35", "4-10", "3-5", "2-2", "8", "5", "2", "1", "0", "3", "5", "1"],
        }
        result = parse_boxscore_stats("401573353", "149", "Montana", athlete, "starters")

        assert result["gid"] == "401573353"
        assert result["MIN"] == 27
        assert result["PTS"] == 35
        assert result["FG_made"] == 4
        assert result["FG_att"] == 10
        assert result["3PT_made"] == 3
        assert result["3PT_att"] == 5
        assert result["FT_made"] == 2
        assert result["FT_att"] == 2
        assert result["starterBench"] == "starters"


class TestParseBoxscore:
    """Tests for parse_boxscore function."""

    def test_parses_boxscore_data(self):
        """Test parsing complete boxscore."""
        data = {
            "bxscr": [
                {
                    "tm": {"id": "149", "dspNm": "Montana"},
                    "stats": [
                        {
                            "type": "starters",
                            "athlts": [
                                {
                                    "athlt": {"id": "1", "dspNm": "Player 1", "pos": "G"},
                                    "stats": ["30", "20", "5-10", "2-5", "3-4", "5", "3", "1"],
                                }
                            ],
                        },
                        {
                            "type": "bench",
                            "athlts": [
                                {
                                    "athlt": {"id": "2", "dspNm": "Player 2", "pos": "F"},
                                    "stats": ["15", "8", "3-6", "1-2", "1-2", "3", "1", "0"],
                                }
                            ],
                        },
                    ],
                }
            ]
        }

        players, boxscores = parse_boxscore("123", data)

        assert len(players) == 2
        assert len(boxscores) == 2
        assert players[0]["athleteName"] == "Player 1"
        assert boxscores[0]["starterBench"] == "starters"
        assert boxscores[1]["starterBench"] == "bench"


class TestParsePlay:
    """Tests for parse_play function."""

    def test_parses_play(self):
        """Test parsing a single play."""
        play = {
            "id": "401573353101806501",
            "period": {"number": 1, "displayValue": "1st Half"},
            "clock": {"displayValue": "19:34"},
            "awayScore": 0,
            "homeScore": 2,
            "homeAway": "home",
            "text": "Casey Jones made Layup.",
            "scoringPlay": True,
        }
        result = parse_play("401573353", play)

        assert result["gid"] == "401573353"
        assert result["id"] == "401573353101806501"
        assert result["period"] == 1
        assert result["periodDisplayValue"] == "1st Half"
        assert result["time"] == "19:34"
        assert result["awayScore"] == 0
        assert result["homeScore"] == 2
        assert result["homeAway"] == "home"
        assert result["description"] == "Casey Jones made Layup."
        assert result["scoringPlay"] is True


class TestParsePlaybyplay:
    """Tests for parse_playbyplay function."""

    def test_parses_multiple_periods(self):
        """Test parsing play-by-play with multiple periods."""
        data = {
            "pbp": {
                "playGrps": [
                    [
                        {"id": "1", "period": {"number": 1}, "clock": {"displayValue": "20:00"}},
                        {"id": "2", "period": {"number": 1}, "clock": {"displayValue": "19:30"}},
                    ],
                    [
                        {"id": "3", "period": {"number": 2}, "clock": {"displayValue": "20:00"}},
                    ],
                ]
            }
        }
        result = parse_playbyplay("123", data)

        assert len(result) == 3
        assert result[0]["id"] == "1"
        assert result[2]["period"] == 2

    def test_handles_empty_data(self):
        """Test handling empty play-by-play data."""
        data = {"pbp": {"playGrps": []}}
        result = parse_playbyplay("123", data)
        assert result == []
