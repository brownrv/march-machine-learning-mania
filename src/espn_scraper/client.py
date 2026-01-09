"""
HTTP client functions for ESPN scraper.

This module handles:
- HTTP requests with retry logic
- Rate limiting (3.5 second delay between requests)
- JSON response handling
"""

import time

import requests


def retry_request(url, headers={}):
    """
    Get a URL and return the request, try it up to 3 times if it fails initially.

    Args:
        url: URL to fetch
        headers: Optional HTTP headers dict

    Returns:
        requests.Response object
    """
    session = requests.Session()
    session.mount("http://", requests.adapters.HTTPAdapter(max_retries=3))
    res = session.get(url=url, allow_redirects=True, headers=headers)
    session.close()
    return res


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def get_new_json(url, headers=None):
    """
    Fetch JSON from a URL with rate limiting.

    This function:
    - Sleeps for 3.5 seconds before making the request (rate limiting)
    - Prints the URL being fetched
    - Returns parsed JSON on success
    - Returns error dict on failure

    Args:
        url: URL to fetch
        headers: HTTP headers (defaults to Chrome user agent)

    Returns:
        dict: Parsed JSON response, or error dict with keys 'url', 'error_code', 'error_msg'
    """
    if headers is None:
        headers = {"User-Agent": DEFAULT_USER_AGENT}
    time.sleep(3.5)
    print(url)
    res = retry_request(url, headers)
    if res.status_code == 200:
        return res.json()
    else:
        print("ERROR:", res.status_code)
        return {"url": url, "error_code": res.status_code, "error_msg": "URL Error"}
