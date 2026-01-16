"""
HTTP client functions for ESPN scraper.

This module handles:
- HTTP requests with retry logic and connection pooling
- Rate limiting (configurable delay between requests)
- Concurrent fetching for related URLs
- JSON response handling
"""

import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Default delay between requests (seconds)
REQUEST_DELAY = 1.0

# Reusable session with connection pooling
_session = None


def get_session():
    """
    Get or create a reusable session with connection pooling and retry logic.

    Retry strategy:
    - 5 total retries (up from 3)
    - Exponential backoff: 2^retry * backoff_factor seconds
      - Retry 1: 2s, Retry 2: 4s, Retry 3: 8s, Retry 4: 16s, Retry 5: 32s
    - Handles 429 (rate limit), 500, 502, 503, 504 errors
    - Respects Retry-After header from server
    """
    global _session
    if _session is None:
        _session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            respect_retry_after_header=True,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10,
        )
        _session.mount("http://", adapter)
        _session.mount("https://", adapter)
    return _session


def reset_session():
    """Reset the session (useful after persistent errors)."""
    global _session
    if _session is not None:
        _session.close()
        _session = None


def retry_request(url, headers=None):
    """
    Get a URL and return the request using pooled session.

    Args:
        url: URL to fetch
        headers: Optional HTTP headers dict

    Returns:
        requests.Response object
    """
    if headers is None:
        headers = {}
    session = get_session()
    return session.get(url=url, allow_redirects=True, headers=headers)


def get_new_json(url, headers=None, delay=None):
    """
    Fetch JSON from a URL with rate limiting.

    This function:
    - Sleeps for configurable delay before making the request (rate limiting)
    - Prints the URL being fetched
    - Returns parsed JSON on success
    - Returns error dict on failure

    Args:
        url: URL to fetch
        headers: HTTP headers (defaults to Chrome user agent)
        delay: Override default delay (seconds), use 0 for no delay

    Returns:
        dict: Parsed JSON response, or error dict with keys 'url', 'error_code', 'error_msg'
    """
    if headers is None:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
    if delay is None:
        delay = REQUEST_DELAY
    if delay > 0:
        time.sleep(delay)
    print(url)
    res = retry_request(url, headers)
    if res.status_code == 200:
        return res.json()
    else:
        print("ERROR:", res.status_code)
        return {"url": url, "error_code": res.status_code, "error_msg": "URL Error"}


def get_multiple_json(urls, headers=None, delay=None, max_workers=3):
    """
    Fetch multiple URLs concurrently with rate limiting.

    Uses a thread pool to fetch URLs in parallel while respecting rate limits.
    Ideal for fetching game, boxscore, and playbyplay for the same game.

    Args:
        urls: List of URLs to fetch
        headers: HTTP headers (defaults to Chrome user agent)
        delay: Delay between requests in each thread (seconds)
        max_workers: Number of concurrent threads (default 3)

    Returns:
        dict: Mapping of URL -> JSON response
    """
    if headers is None:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
    if delay is None:
        delay = REQUEST_DELAY

    results = {}

    def fetch_one(url):
        # Add jitter (0-50% of delay) to avoid thundering herd
        jitter = random.uniform(0, delay * 0.5)
        time.sleep(delay + jitter)
        print(url)
        res = retry_request(url, headers)
        if res.status_code == 200:
            return url, res.json()
        else:
            print("ERROR:", res.status_code)
            return url, {"url": url, "error_code": res.status_code, "error_msg": "URL Error"}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, url): url for url in urls}
        for future in as_completed(futures):
            url, data = future.result()
            results[url] = data

    return results
