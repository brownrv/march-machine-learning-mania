"""
Unit tests for ESPN scraper league and season functions.
"""

import pytest

from espn_scraper.leagues import (
    get_available_seasons,
    get_current_season_year,
    get_leagues,
    get_ncw_groups,
    get_season,
    get_season_start_end_dates,
)


class TestLeagueFunctions:
    """Test league metadata functions"""

    def test_get_leagues(self):
        leagues = get_leagues()
        assert leagues == ["mens-college-basketball", "womens-college-basketball"]
        assert len(leagues) == 2

    def test_get_ncw_groups(self):
        groups = get_ncw_groups()
        assert isinstance(groups, list)
        assert len(groups) > 0
        assert 1 in groups
        assert 50 in groups
        # Groups should be unique
        assert len(groups) == len(set(groups))


class TestSeasonFunctions:
    """Test season-related functions"""

    def test_get_current_season_year_mens(self):
        season = get_current_season_year("mens-college-basketball")
        assert isinstance(season, int)
        # Current season should be 2025 or 2026 depending on month
        assert season >= 2025

    def test_get_current_season_year_womens(self):
        season = get_current_season_year("womens-college-basketball")
        assert isinstance(season, int)
        assert season >= 2025

    def test_get_available_seasons_mens(self):
        seasons = get_available_seasons("mens-college-basketball")
        assert isinstance(seasons, list)
        assert "2003" in seasons  # First season
        assert "2024" in seasons
        # All seasons should be 4-digit strings
        assert all(len(s) == 4 and s.isdigit() for s in seasons)

    def test_get_available_seasons_womens(self):
        seasons = get_available_seasons("womens-college-basketball")
        assert isinstance(seasons, list)
        assert "2003" in seasons
        assert "2024" in seasons

    def test_get_available_seasons_invalid_league(self):
        with pytest.raises(ValueError, match="Unknown league"):
            get_available_seasons("invalid-league")

    def test_get_season_from_season_year(self):
        season = get_season("mens-college-basketball", "2024")
        assert season == "2024"

    def test_get_season_from_date_november(self):
        # November 2023 -> 2024 season
        season = get_season("mens-college-basketball", "20231115")
        assert season == "2024"

    def test_get_season_from_date_march(self):
        # March 2024 -> 2024 season
        season = get_season("mens-college-basketball", "20240315")
        assert season == "2024"

    def test_get_season_from_date_april(self):
        # April 2024 -> 2024 season
        season = get_season("mens-college-basketball", "20240415")
        assert season == "2024"

    def test_get_season_from_date_may(self):
        # May 2024 -> 2025 season
        season = get_season("mens-college-basketball", "20240515")
        assert season == "2025"

    def test_get_season_from_date_range(self):
        # Date range with hyphen -> use first date
        season = get_season("mens-college-basketball", "20240101-20240331")
        assert season == "2024"

    def test_get_season_start_end_dates(self):
        start, end = get_season_start_end_dates("mens-college-basketball", "2024")
        assert start == "20231101"  # Nov 1, 2023
        # End date should be April 30, 2024 or earlier (if current date is before that)
        assert end <= "20240430"
        assert len(end) == 8  # YYYYMMDD format

    def test_get_season_start_end_dates_invalid_season(self):
        with pytest.raises(ValueError, match="data is not available"):
            get_season_start_end_dates("mens-college-basketball", "1999")

    def test_get_season_start_end_dates_invalid_league(self):
        with pytest.raises(ValueError, match="Unknown league"):
            get_season_start_end_dates("invalid-league", "2024")
