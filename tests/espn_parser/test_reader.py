"""Tests for espn_parser.reader module."""

import json

import pytest

from espn_parser.reader import (
    count_files,
    list_cached_seasons,
    read_boxscores,
    read_games,
    read_json,
    read_playbyplay,
    read_schedules,
)


class TestReadJson:
    """Tests for read_json function."""

    def test_reads_valid_json(self, tmp_path):
        """Test reading valid JSON file."""
        file_path = tmp_path / "test.json"
        file_path.write_text('{"key": "value"}')

        result = read_json(file_path)
        assert result == {"key": "value"}

    def test_reads_json_array(self, tmp_path):
        """Test reading JSON array."""
        file_path = tmp_path / "test.json"
        file_path.write_text('[{"id": 1}, {"id": 2}]')

        result = read_json(file_path)
        assert result == [{"id": 1}, {"id": 2}]

    def test_nonexistent_file_returns_none(self, tmp_path):
        """Test that nonexistent file returns None."""
        file_path = tmp_path / "nonexistent.json"
        result = read_json(file_path)
        assert result is None

    def test_invalid_json_returns_none(self, tmp_path):
        """Test that invalid JSON returns None."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("not valid json {")

        result = read_json(file_path)
        assert result is None

    def test_error_msg_file_returns_none(self, tmp_path):
        """Test that file with error_msg returns None."""
        file_path = tmp_path / "error.json"
        file_path.write_text('{"error_msg": "Some error occurred"}')

        result = read_json(file_path)
        assert result is None


class TestReadSchedules:
    """Tests for read_schedules function."""

    def test_reads_schedule_files(self, tmp_path):
        """Test reading schedule files."""
        # Create directory structure
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "schedule"
        dir_path.mkdir(parents=True)

        # Create test files
        (dir_path / "20231106.json").write_text('[{"id": "1"}]')
        (dir_path / "20231107.json").write_text('[{"id": "2"}]')

        results = list(read_schedules("mens-college-basketball", "2024", tmp_path))

        assert len(results) == 2
        assert results[0] == ("20231106", [{"id": "1"}])
        assert results[1] == ("20231107", [{"id": "2"}])

    def test_skips_empty_arrays(self, tmp_path):
        """Test that empty array files are still yielded."""
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "schedule"
        dir_path.mkdir(parents=True)

        (dir_path / "20231101.json").write_text("[]")

        results = list(read_schedules("mens-college-basketball", "2024", tmp_path))

        # Empty array is still a valid list, just with no events
        assert len(results) == 1
        assert results[0] == ("20231101", [])

    def test_skips_non_list_files(self, tmp_path):
        """Test that non-list files are skipped."""
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "schedule"
        dir_path.mkdir(parents=True)

        (dir_path / "20231106.json").write_text('{"not": "a list"}')

        results = list(read_schedules("mens-college-basketball", "2024", tmp_path))
        assert len(results) == 0


class TestReadGames:
    """Tests for read_games function."""

    def test_reads_game_files(self, tmp_path):
        """Test reading game files."""
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "game"
        dir_path.mkdir(parents=True)

        (dir_path / "401573353.json").write_text('{"gmInfo": {}}')
        (dir_path / "401573354.json").write_text('{"gmInfo": {}}')

        results = list(read_games("mens-college-basketball", "2024", tmp_path))

        assert len(results) == 2
        game_ids = [r[0] for r in results]
        assert "401573353" in game_ids
        assert "401573354" in game_ids


class TestReadBoxscores:
    """Tests for read_boxscores function."""

    def test_reads_boxscore_files(self, tmp_path):
        """Test reading boxscore files."""
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "boxscore"
        dir_path.mkdir(parents=True)

        (dir_path / "401573353.json").write_text('{"bxscr": []}')

        results = list(read_boxscores("mens-college-basketball", "2024", tmp_path))

        assert len(results) == 1
        assert results[0][0] == "401573353"


class TestReadPlaybyplay:
    """Tests for read_playbyplay function."""

    def test_reads_playbyplay_files(self, tmp_path):
        """Test reading play-by-play files."""
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "playbyplay"
        dir_path.mkdir(parents=True)

        (dir_path / "401573353.json").write_text('{"pbp": {"playGrps": []}}')

        results = list(read_playbyplay("mens-college-basketball", "2024", tmp_path))

        assert len(results) == 1
        assert results[0][0] == "401573353"


class TestListCachedSeasons:
    """Tests for list_cached_seasons function."""

    def test_lists_seasons(self, tmp_path):
        """Test listing cached seasons."""
        # Create season directories
        (tmp_path / "mens-college-basketball" / "2023").mkdir(parents=True)
        (tmp_path / "mens-college-basketball" / "2024").mkdir(parents=True)
        (tmp_path / "mens-college-basketball" / "2025").mkdir(parents=True)

        results = list_cached_seasons("mens-college-basketball", tmp_path)

        assert results == ["2023", "2024", "2025"]

    def test_returns_sorted(self, tmp_path):
        """Test that seasons are returned sorted."""
        # Create in non-sorted order
        (tmp_path / "mens-college-basketball" / "2025").mkdir(parents=True)
        (tmp_path / "mens-college-basketball" / "2023").mkdir(parents=True)
        (tmp_path / "mens-college-basketball" / "2024").mkdir(parents=True)

        results = list_cached_seasons("mens-college-basketball", tmp_path)

        assert results == ["2023", "2024", "2025"]

    def test_ignores_non_year_directories(self, tmp_path):
        """Test that non-year directories are ignored."""
        (tmp_path / "mens-college-basketball" / "2024").mkdir(parents=True)
        (tmp_path / "mens-college-basketball" / "temp").mkdir(parents=True)
        (tmp_path / "mens-college-basketball" / "12345").mkdir(parents=True)  # 5 digits

        results = list_cached_seasons("mens-college-basketball", tmp_path)

        assert results == ["2024"]

    def test_nonexistent_league_returns_empty(self, tmp_path):
        """Test that nonexistent league returns empty list."""
        results = list_cached_seasons("nonexistent-league", tmp_path)
        assert results == []


class TestCountFiles:
    """Tests for count_files function."""

    def test_counts_json_files(self, tmp_path):
        """Test counting JSON files."""
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "game"
        dir_path.mkdir(parents=True)

        (dir_path / "1.json").write_text("{}")
        (dir_path / "2.json").write_text("{}")
        (dir_path / "3.json").write_text("{}")

        result = count_files("mens-college-basketball", "2024", "game", tmp_path)
        assert result == 3

    def test_nonexistent_directory_returns_zero(self, tmp_path):
        """Test that nonexistent directory returns 0."""
        result = count_files("mens-college-basketball", "2024", "game", tmp_path)
        assert result == 0
