"""Tests for espn_parser.paths module."""

from pathlib import Path

import pytest

from espn_parser.paths import (
    DEFAULT_PARSED_BASE,
    DEFAULT_RAW_BASE,
    PARSED_FILES,
    RAW_DATA_TYPES,
    ensure_parsed_dir,
    get_parsed_path,
    get_raw_path,
    list_raw_files,
)


class TestGetRawPath:
    """Tests for get_raw_path function."""

    def test_league_and_season_only(self):
        """Test path with just league and season."""
        path = get_raw_path("mens-college-basketball", "2024")
        assert path == DEFAULT_RAW_BASE / "mens-college-basketball" / "2024"

    def test_with_data_type(self):
        """Test path with data type."""
        path = get_raw_path("mens-college-basketball", "2024", "schedule")
        assert path == DEFAULT_RAW_BASE / "mens-college-basketball" / "2024" / "schedule"

    def test_with_file_id(self):
        """Test path with file ID."""
        path = get_raw_path("mens-college-basketball", "2024", "game", "401573353")
        expected = DEFAULT_RAW_BASE / "mens-college-basketball" / "2024" / "game" / "401573353.json"
        assert path == expected

    def test_custom_base_path(self):
        """Test with custom base path."""
        path = get_raw_path("mens-college-basketball", "2024", base_path="/custom/path")
        assert path == Path("/custom/path") / "mens-college-basketball" / "2024"

    def test_invalid_data_type_raises(self):
        """Test that invalid data type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid data_type"):
            get_raw_path("mens-college-basketball", "2024", "invalid_type")

    def test_file_id_without_data_type_raises(self):
        """Test that file_id without data_type raises ValueError."""
        with pytest.raises(ValueError, match="data_type is required"):
            get_raw_path("mens-college-basketball", "2024", file_id="123")

    def test_all_raw_data_types_valid(self):
        """Test all RAW_DATA_TYPES are accepted."""
        for data_type in RAW_DATA_TYPES:
            path = get_raw_path("mens-college-basketball", "2024", data_type)
            assert data_type in str(path)


class TestGetParsedPath:
    """Tests for get_parsed_path function."""

    def test_league_and_season_only(self):
        """Test path with just league and season."""
        path = get_parsed_path("mens-college-basketball", "2024")
        assert path == DEFAULT_PARSED_BASE / "mens-college-basketball" / "2024"

    def test_with_file_name(self):
        """Test path with file name."""
        path = get_parsed_path("mens-college-basketball", "2024", "games")
        expected = DEFAULT_PARSED_BASE / "mens-college-basketball" / "2024" / "games.parquet"
        assert path == expected

    def test_custom_base_path(self):
        """Test with custom base path."""
        path = get_parsed_path("mens-college-basketball", "2024", base_path="/custom/output")
        assert path == Path("/custom/output") / "mens-college-basketball" / "2024"

    def test_invalid_file_name_raises(self):
        """Test that invalid file name raises ValueError."""
        with pytest.raises(ValueError, match="Invalid file_name"):
            get_parsed_path("mens-college-basketball", "2024", "invalid_file")

    def test_all_parsed_files_valid(self):
        """Test all PARSED_FILES are accepted."""
        for file_name in PARSED_FILES:
            path = get_parsed_path("mens-college-basketball", "2024", file_name)
            assert path.suffix == ".parquet"
            assert file_name in str(path)


class TestListRawFiles:
    """Tests for list_raw_files function."""

    def test_nonexistent_directory_returns_empty(self, tmp_path):
        """Test that nonexistent directory returns empty list."""
        result = list_raw_files(
            "mens-college-basketball", "2024", "schedule", base_path=tmp_path
        )
        assert result == []

    def test_lists_json_files(self, tmp_path):
        """Test listing JSON files in directory."""
        # Create test directory structure
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "schedule"
        dir_path.mkdir(parents=True)

        # Create test files
        (dir_path / "20231106.json").write_text("{}")
        (dir_path / "20231107.json").write_text("{}")
        (dir_path / "not_json.txt").write_text("ignore")

        result = list_raw_files(
            "mens-college-basketball", "2024", "schedule", base_path=tmp_path
        )

        assert len(result) == 2
        assert all(f.suffix == ".json" for f in result)

    def test_returns_sorted_paths(self, tmp_path):
        """Test that returned paths are sorted."""
        dir_path = tmp_path / "mens-college-basketball" / "2024" / "schedule"
        dir_path.mkdir(parents=True)

        # Create files in non-sorted order
        (dir_path / "20231108.json").write_text("{}")
        (dir_path / "20231106.json").write_text("{}")
        (dir_path / "20231107.json").write_text("{}")

        result = list_raw_files(
            "mens-college-basketball", "2024", "schedule", base_path=tmp_path
        )

        assert [f.stem for f in result] == ["20231106", "20231107", "20231108"]


class TestEnsureParsedDir:
    """Tests for ensure_parsed_dir function."""

    def test_creates_directory(self, tmp_path):
        """Test that directory is created."""
        result = ensure_parsed_dir("mens-college-basketball", "2024", base_path=tmp_path)

        assert result.exists()
        assert result.is_dir()
        assert result == tmp_path / "mens-college-basketball" / "2024"

    def test_returns_existing_directory(self, tmp_path):
        """Test that existing directory is returned without error."""
        dir_path = tmp_path / "mens-college-basketball" / "2024"
        dir_path.mkdir(parents=True)

        result = ensure_parsed_dir("mens-college-basketball", "2024", base_path=tmp_path)

        assert result == dir_path
