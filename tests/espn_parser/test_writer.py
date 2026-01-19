"""Tests for espn_parser.writer module."""

import pandas as pd
import pytest

from espn_parser.writer import (
    write_boxscores,
    write_events,
    write_games,
    write_parquet,
    write_players,
    write_playbyplay,
    write_teams,
    write_venues,
)


class TestWriteParquet:
    """Tests for write_parquet function."""

    def test_writes_parquet_file(self, tmp_path):
        """Test writing a parquet file."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})

        result = write_parquet(df, "mens-college-basketball", "2024", "games", tmp_path)

        assert result.exists()
        assert result.suffix == ".parquet"

        # Verify contents
        loaded = pd.read_parquet(result)
        pd.testing.assert_frame_equal(loaded, df)

    def test_creates_directory(self, tmp_path):
        """Test that directory is created if it doesn't exist."""
        df = pd.DataFrame({"a": [1]})

        result = write_parquet(df, "mens-college-basketball", "2024", "events", tmp_path)

        assert result.parent.exists()


class TestWriteEvents:
    """Tests for write_events function."""

    def test_writes_events(self, tmp_path):
        """Test writing events parquet."""
        records = [
            {"id": "1", "date": "2024-01-01", "link": "/game/1", "completed": True},
            {"id": "2", "date": "2024-01-02", "link": "/game/2", "completed": False},
        ]

        result = write_events(records, "mens-college-basketball", "2024", tmp_path)

        assert result.exists()
        df = pd.read_parquet(result)
        assert len(df) == 2
        assert "neutralSite" in df.columns  # Added missing column

    def test_handles_missing_columns(self, tmp_path):
        """Test that missing columns are added."""
        records = [{"id": "1"}]  # Minimal record

        result = write_events(records, "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert "date" in df.columns
        assert "completed" in df.columns


class TestWriteGames:
    """Tests for write_games function."""

    def test_writes_games(self, tmp_path):
        """Test writing games parquet."""
        records = [
            {
                "gid": "123",
                "dtTm": "2024-01-01",
                "gameState": "post",
                "tm1_id": "1",
                "tm2_id": "2",
            }
        ]

        result = write_games(records, "mens-college-basketball", "2024", tmp_path)

        assert result.exists()
        df = pd.read_parquet(result)
        assert len(df) == 1


class TestWriteTeams:
    """Tests for write_teams function."""

    def test_deduplicates_teams(self, tmp_path):
        """Test that teams are deduplicated by ID."""
        records = [
            {"id": "1", "displayName": "Team A"},
            {"id": "1", "displayName": "Team A Updated"},  # Duplicate ID
            {"id": "2", "displayName": "Team B"},
        ]

        result = write_teams(records, "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 2  # Only 2 unique teams

    def test_keeps_first_occurrence(self, tmp_path):
        """Test that first occurrence is kept when deduplicating."""
        records = [
            {"id": "1", "displayName": "First"},
            {"id": "1", "displayName": "Second"},
        ]

        result = write_teams(records, "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert df[df["id"] == "1"]["displayName"].iloc[0] == "First"

    def test_sorts_by_id(self, tmp_path):
        """Test that teams are sorted by ID."""
        records = [
            {"id": "3", "displayName": "Team C"},
            {"id": "1", "displayName": "Team A"},
            {"id": "2", "displayName": "Team B"},
        ]

        result = write_teams(records, "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert df["id"].tolist() == ["1", "2", "3"]


class TestWriteVenues:
    """Tests for write_venues function."""

    def test_deduplicates_venues(self, tmp_path):
        """Test that venues are deduplicated by ID."""
        records = [
            {"id": "1", "fullName": "Arena A"},
            {"id": "1", "fullName": "Arena A"},  # Duplicate
            {"id": "2", "fullName": "Arena B"},
        ]

        result = write_venues(records, "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 2

    def test_handles_empty_records(self, tmp_path):
        """Test handling empty records list."""
        result = write_venues([], "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 0
        assert "fullName" in df.columns


class TestWritePlayers:
    """Tests for write_players function."""

    def test_deduplicates_by_aid(self, tmp_path):
        """Test that players are deduplicated by athlete ID."""
        records = [
            {"aid": "1", "athleteName": "Player A", "tid": "10"},
            {"aid": "1", "athleteName": "Player A", "tid": "10"},  # Duplicate
            {"aid": "2", "athleteName": "Player B", "tid": "10"},
        ]

        result = write_players(records, "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 2

    def test_handles_empty_records(self, tmp_path):
        """Test handling empty records list."""
        result = write_players([], "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 0


class TestWriteBoxscores:
    """Tests for write_boxscores function."""

    def test_writes_boxscores(self, tmp_path):
        """Test writing boxscores parquet."""
        records = [
            {"gid": "1", "aid": "100", "PTS": 20},
            {"gid": "1", "aid": "101", "PTS": 15},
        ]

        result = write_boxscores(records, "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 2

    def test_handles_empty_records(self, tmp_path):
        """Test handling empty records list."""
        result = write_boxscores([], "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 0


class TestWritePlaybyplay:
    """Tests for write_playbyplay function."""

    def test_writes_playbyplay(self, tmp_path):
        """Test writing play-by-play parquet."""
        records = [
            {"gid": "1", "id": "play1", "period": 1, "time": "20:00"},
            {"gid": "1", "id": "play2", "period": 1, "time": "19:45"},
        ]

        result = write_playbyplay(records, "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 2

    def test_handles_empty_records(self, tmp_path):
        """Test handling empty records list."""
        result = write_playbyplay([], "mens-college-basketball", "2024", tmp_path)

        df = pd.read_parquet(result)
        assert len(df) == 0
