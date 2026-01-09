"""
Cache management functions for ESPN scraper.

This module handles:
- Computing cache file paths
- Reading/writing JSON files
- Validating cached files
"""

import json
import os.path

from .urls import get_data_type_id_from_url


def get_filename(cached_json_path, league, season, data_type, url):
    """
    Compute cache filename for a given URL.

    Creates directory structure if it doesn't exist:
    {cached_json_path}/{league}/{season}/{data_type}/{data_type_id}.json

    Args:
        cached_json_path: Base cache directory path
        league: League identifier
        season: Season year
        data_type: Type of data (schedule, scoreboard, game, boxscore, playbyplay)
        url: URL being cached (used to extract data_type_id)

    Returns:
        str: Full path to cache file
    """
    # add slash if necessary to cached_json_path
    if cached_json_path[-1] != "/":
        cached_json_path += "/"
    dir_path = cached_json_path + "/" + league + "/" + season + "/" + data_type + "/"
    data_type_id = get_data_type_id_from_url(url)
    # create a league directory and data_type directory in cached_json if doesn't already exist
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    filename = dir_path + data_type_id + ".json"
    return filename


def get_cached(filename):
    """
    Load JSON data from cache file.

    Args:
        filename: Path to cache file

    Returns:
        dict: Parsed JSON data, or None if file doesn't exist
    """
    data = None
    if os.path.isfile(filename):
        with open(filename) as json_data:
            data = json.load(json_data)
    return data


def is_cached(filename):
    """
    Check if a file is properly cached.

    A file is considered properly cached if:
    - File exists
    - File is valid JSON
    - File does not contain 'error_msg' key

    Args:
        filename: Path to cache file

    Returns:
        bool: True if file is properly cached, False otherwise
    """
    # Check if the file exists
    if os.path.isfile(filename):
        try:
            # Attempt to open and parse the JSON file
            with open(filename, "r", encoding="utf-8", errors="ignore") as file:
                data = json.load(file)
            # Check if 'error_msg' key is not present in the JSON object
            if "error_msg" not in data:
                return True
            else:
                print("File contains 'error_msg'.")
                return False
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {filename}: {e}")
            return False
    else:
        print("File does not exist.")
        return False


def write_cache(filename, data):
    """
    Write data to cache file as JSON.

    Args:
        filename: Path to cache file
        data: Data to write (will be JSON-serialized)
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
