"""
Tests for ESPN scraper cache management.
"""



from espn_scraper.cache import get_cached, get_filename, is_cached, write_cache


class TestCacheFilenames:
    """Test cache filename generation"""

    def test_get_filename_schedule(self):
        url = "https://www.espn.com/mens-college-basketball/schedule/_/date/20240315&_xhr=1"
        filename = get_filename("cache", "mens-college-basketball", "2024", "schedule", url)
        assert "cache" in filename
        assert "mens-college-basketball" in filename
        assert "2024" in filename
        assert "schedule" in filename
        assert "20240315.json" in filename

    def test_get_filename_game(self):
        url = "https://www.espn.com/womens-college-basketball/game/_/gameId/401635566&_xhr=1"
        filename = get_filename("data", "womens-college-basketball", "2025", "game", url)
        assert "data" in filename
        assert "womens-college-basketball" in filename
        assert "2025" in filename
        assert "game" in filename
        assert "401635566.json" in filename


class TestCacheOperations:
    """Test cache read/write operations"""

    def test_write_and_read_cache(self, tmp_path):
        # Create test data
        test_data = {"team1": "Duke", "team2": "UNC", "score": "79-68"}

        # Write to cache
        cache_file = tmp_path / "test.json"
        write_cache(str(cache_file), test_data)

        # Verify file exists
        assert cache_file.exists()

        # Read from cache
        loaded_data = get_cached(str(cache_file))
        assert loaded_data == test_data

    def test_get_cached_nonexistent_file(self):
        result = get_cached("/nonexistent/path/file.json")
        assert result is None

    def test_is_cached_valid_file(self, tmp_path):
        # Create valid cache file
        cache_file = tmp_path / "valid.json"
        write_cache(str(cache_file), {"game_id": "12345"})

        assert is_cached(str(cache_file)) is True

    def test_is_cached_file_with_error_msg(self, tmp_path):
        # Create cache file with error_msg key (should be treated as invalid)
        cache_file = tmp_path / "error.json"
        write_cache(str(cache_file), {"error_msg": "URL Error", "error_code": 404})

        # Should return False because file contains error_msg
        assert is_cached(str(cache_file)) is False

    def test_is_cached_nonexistent_file(self):
        assert is_cached("/nonexistent/path/file.json") is False

    def test_is_cached_invalid_json(self, tmp_path):
        # Create file with invalid JSON
        cache_file = tmp_path / "invalid.json"
        cache_file.write_text("not valid json{{{")

        assert is_cached(str(cache_file)) is False

    def test_write_cache_creates_complex_data(self, tmp_path):
        # Test with complex nested data
        complex_data = {
            "events": [
                {"id": "123", "teams": ["Duke", "UNC"]},
                {"id": "456", "teams": ["Kansas", "Kentucky"]},
            ],
            "metadata": {"season": "2024", "league": "mens-college-basketball"},
        }

        cache_file = tmp_path / "complex.json"
        write_cache(str(cache_file), complex_data)

        # Verify it can be read back
        loaded = get_cached(str(cache_file))
        assert loaded == complex_data
        assert len(loaded["events"]) == 2
