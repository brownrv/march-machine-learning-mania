"""
Unit tests for ESPN scraper URL builders and parsers.

These are pure function tests with no I/O dependencies.
"""

import pytest

from espn_scraper.urls import (
    get_boxscore_url,
    get_data_type_from_url,
    get_data_type_id_from_url,
    get_game_url,
    get_league_from_url,
    get_playbyplay_url,
    get_schedule_url,
    get_scoreboard_url,
)


class TestURLBuilders:
    """Test URL building functions"""

    def test_get_schedule_url(self):
        url = get_schedule_url("mens-college-basketball", "20240315")
        assert url == "https://www.espn.com/mens-college-basketball/schedule/_/date/20240315&_xhr=1"

    def test_get_scoreboard_url_no_group(self):
        url = get_scoreboard_url("mens-college-basketball", "20240315")
        assert (
            url == "https://www.espn.com/mens-college-basketball/scoreboard/_/date/20240315&_xhr=1"
        )

    def test_get_scoreboard_url_with_group(self):
        # Note: is_scoreboard_season returns False for all current cases,
        # so group parameter is ignored
        url = get_scoreboard_url("womens-college-basketball", "20220315", group=1)
        assert (
            url
            == "https://www.espn.com/womens-college-basketball/scoreboard/_/date/20220315&_xhr=1"
        )

    def test_get_game_url(self):
        url = get_game_url("mens-college-basketball", "401635566")
        assert url == "https://www.espn.com/mens-college-basketball/game/_/gameId/401635566&_xhr=1"

    def test_get_boxscore_url(self):
        url = get_boxscore_url("womens-college-basketball", "401635566")
        assert (
            url
            == "https://www.espn.com/womens-college-basketball/boxscore/_/gameId/401635566&_xhr=1"
        )

    def test_get_playbyplay_url(self):
        url = get_playbyplay_url("mens-college-basketball", "401635566")
        assert (
            url
            == "https://www.espn.com/mens-college-basketball/playbyplay/_/gameId/401635566&_xhr=1"
        )


class TestURLParsers:
    """Test URL parsing functions"""

    def test_get_league_from_url(self):
        url = "https://www.espn.com/mens-college-basketball/schedule/_/date/20240315&_xhr=1"
        assert get_league_from_url(url) == "mens-college-basketball"

    def test_get_league_from_url_womens(self):
        url = "https://www.espn.com/womens-college-basketball/game/_/gameId/401635566&_xhr=1"
        assert get_league_from_url(url) == "womens-college-basketball"

    def test_get_data_type_from_url_schedule(self):
        url = "https://www.espn.com/mens-college-basketball/schedule/_/date/20240315&_xhr=1"
        assert get_data_type_from_url(url) == "schedule"

    def test_get_data_type_from_url_scoreboard(self):
        url = "https://www.espn.com/mens-college-basketball/scoreboard/_/date/20240315&_xhr=1"
        assert get_data_type_from_url(url) == "scoreboard"

    def test_get_data_type_from_url_game(self):
        url = "https://www.espn.com/mens-college-basketball/game/_/gameId/401635566&_xhr=1"
        assert get_data_type_from_url(url) == "game"

    def test_get_data_type_from_url_boxscore(self):
        url = "https://www.espn.com/mens-college-basketball/boxscore/_/gameId/401635566&_xhr=1"
        assert get_data_type_from_url(url) == "boxscore"

    def test_get_data_type_from_url_playbyplay(self):
        url = "https://www.espn.com/mens-college-basketball/playbyplay/_/gameId/401635566&_xhr=1"
        assert get_data_type_from_url(url) == "playbyplay"

    def test_get_data_type_from_url_invalid(self):
        url = "https://www.espn.com/mens-college-basketball/invalid/_/date/20240315&_xhr=1"
        with pytest.raises(ValueError, match="Unknown data_type for url"):
            get_data_type_from_url(url)

    def test_get_data_type_id_from_url_schedule(self):
        url = "https://www.espn.com/mens-college-basketball/schedule/_/date/20240315&_xhr=1"
        assert get_data_type_id_from_url(url) == "20240315"

    def test_get_data_type_id_from_url_game(self):
        url = "https://www.espn.com/mens-college-basketball/game/_/gameId/401635566&_xhr=1"
        assert get_data_type_id_from_url(url) == "401635566"

    def test_get_data_type_id_from_url_scoreboard(self):
        url = "https://www.espn.com/mens-college-basketball/scoreboard/_/date/20240315/group/50&_xhr=1"
        # Scoreboard with group uses special format: date_group
        assert get_data_type_id_from_url(url) == "20240315_50"
