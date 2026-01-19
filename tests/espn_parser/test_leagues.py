"""Tests for espn_parser.leagues module."""

import pytest

from espn_parser.leagues import (
    get_available_seasons,
    get_current_season_year,
    get_leagues,
    validate_league,
    validate_season,
)


class TestGetLeagues:
    """Tests for get_leagues function."""

    def test_returns_list(self):
        """Test that get_leagues returns a list."""
        result = get_leagues()
        assert isinstance(result, list)

    def test_contains_mens_basketball(self):
        """Test that men's basketball is included."""
        result = get_leagues()
        assert "mens-college-basketball" in result

    def test_contains_womens_basketball(self):
        """Test that women's basketball is included."""
        result = get_leagues()
        assert "womens-college-basketball" in result


class TestGetCurrentSeasonYear:
    """Tests for get_current_season_year function."""

    def test_returns_integer(self):
        """Test that current season year is an integer."""
        result = get_current_season_year("mens-college-basketball")
        assert isinstance(result, int)

    def test_valid_year_range(self):
        """Test that year is reasonable."""
        result = get_current_season_year("mens-college-basketball")
        assert 2020 <= result <= 2030

    def test_unknown_league_raises(self):
        """Test that unknown league raises ValueError."""
        with pytest.raises(ValueError, match="Unknown league"):
            get_current_season_year("invalid-league")


class TestGetAvailableSeasons:
    """Tests for get_available_seasons function."""

    def test_returns_list(self):
        """Test that available seasons is a list."""
        result = get_available_seasons("mens-college-basketball")
        assert isinstance(result, list)

    def test_starts_with_2003(self):
        """Test that seasons start with 2003."""
        result = get_available_seasons("mens-college-basketball")
        assert result[0] == "2003"

    def test_seasons_are_strings(self):
        """Test that seasons are strings."""
        result = get_available_seasons("mens-college-basketball")
        assert all(isinstance(s, str) for s in result)

    def test_seasons_are_four_digits(self):
        """Test that seasons are four-digit strings."""
        result = get_available_seasons("mens-college-basketball")
        assert all(len(s) == 4 and s.isdigit() for s in result)

    def test_unknown_league_raises(self):
        """Test that unknown league raises ValueError."""
        with pytest.raises(ValueError, match="Unknown league"):
            get_available_seasons("invalid-league")


class TestValidateLeague:
    """Tests for validate_league function."""

    def test_valid_league_returns_league(self):
        """Test that valid league is returned."""
        result = validate_league("mens-college-basketball")
        assert result == "mens-college-basketball"

    def test_invalid_league_raises(self):
        """Test that invalid league raises ValueError."""
        with pytest.raises(ValueError, match="Unknown league"):
            validate_league("invalid-league")


class TestValidateSeason:
    """Tests for validate_season function."""

    def test_valid_season_returns_season(self):
        """Test that valid season is returned."""
        result = validate_season("mens-college-basketball", "2024")
        assert result == "2024"

    def test_invalid_season_raises(self):
        """Test that invalid season raises ValueError."""
        with pytest.raises(ValueError, match="not available"):
            validate_season("mens-college-basketball", "1900")
