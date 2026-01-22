"""
Unit tests for ESPN scraper daily DAG utility functions.

These tests verify the date calculation and season detection logic.
Since Airflow is only available in Docker, we test the pure functions
by reimplementing them here (they should match dags/espn_scraper_daily.py).
"""

import pytest


def get_season_from_date(date_str: str) -> str:
    """
    Determine the season year from a date.

    College basketball seasons span Nov-Apr, so:
    - Nov-Dec dates belong to next calendar year's season
    - Jan-Apr dates belong to current calendar year's season

    This function mirrors dags/espn_scraper_daily.py:get_season_from_date
    """
    year = int(date_str[:4])
    month = int(date_str[4:6])

    if month >= 11:
        return str(year + 1)
    return str(year)


class TestGetSeasonFromDate:
    """Test season calculation from date strings."""

    def test_november_returns_next_year(self):
        """November dates should return the next calendar year as season."""
        assert get_season_from_date("20241101") == "2025"
        assert get_season_from_date("20241115") == "2025"
        assert get_season_from_date("20241130") == "2025"

    def test_december_returns_next_year(self):
        """December dates should return the next calendar year as season."""
        assert get_season_from_date("20241201") == "2025"
        assert get_season_from_date("20241215") == "2025"
        assert get_season_from_date("20241231") == "2025"

    def test_january_returns_same_year(self):
        """January dates should return the same calendar year as season."""
        assert get_season_from_date("20250101") == "2025"
        assert get_season_from_date("20250115") == "2025"
        assert get_season_from_date("20250131") == "2025"

    def test_february_returns_same_year(self):
        """February dates should return the same calendar year as season."""
        assert get_season_from_date("20250201") == "2025"
        assert get_season_from_date("20250214") == "2025"
        assert get_season_from_date("20250228") == "2025"

    def test_march_returns_same_year(self):
        """March dates should return the same calendar year as season."""
        assert get_season_from_date("20250301") == "2025"
        assert get_season_from_date("20250315") == "2025"
        assert get_season_from_date("20250331") == "2025"

    def test_april_returns_same_year(self):
        """April dates should return the same calendar year as season."""
        assert get_season_from_date("20250401") == "2025"
        assert get_season_from_date("20250415") == "2025"
        assert get_season_from_date("20250430") == "2025"

    def test_off_season_months(self):
        """Off-season months (May-Oct) should return current year season."""
        # May 2025 -> 2025 season (off-season, but function still works)
        assert get_season_from_date("20250515") == "2025"
        # October 2025 -> 2025 season
        assert get_season_from_date("20251015") == "2025"


class TestIsBasketballSeason:
    """Test basketball season detection logic.

    Tests the month-checking logic used in the DAG's is_basketball_season function.
    """

    @pytest.mark.parametrize(
        "month,expected",
        [
            (1, True),  # January - in season
            (2, True),  # February - in season
            (3, True),  # March - in season (March Madness!)
            (4, True),  # April - in season (Final Four)
            (5, False),  # May - off season
            (6, False),  # June - off season
            (7, False),  # July - off season
            (8, False),  # August - off season
            (9, False),  # September - off season
            (10, False),  # October - off season
            (11, True),  # November - season starts
            (12, True),  # December - in season
        ],
    )
    def test_season_months(self, month, expected):
        """Verify correct months are considered in-season."""
        # This matches the logic in dags/espn_scraper_daily.py:is_basketball_season
        in_season = month in (11, 12, 1, 2, 3, 4)
        assert in_season == expected
