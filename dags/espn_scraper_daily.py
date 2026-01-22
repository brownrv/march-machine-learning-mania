"""
Daily ESPN Basketball Scraper DAG.

This DAG scrapes ESPN data for both men's and women's college basketball
every day from November through April (the college basketball season).

Features:
- Runs daily at 6 AM UTC
- Scrapes yesterday's games (to ensure complete data)
- Auto-detects the correct season based on current date
- Only active during Nov-Apr (pauses during off-season months)
- Scrapes both leagues in parallel
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator


def is_basketball_season(**context) -> bool:
    """
    Check if current date is within college basketball season (Nov 1 - Apr 30).

    Returns True if in season, False otherwise (short-circuits the DAG).
    """
    import logging

    scrape_date = get_scrape_date(**context)
    month = int(scrape_date[4:6])

    in_season = month in (11, 12, 1, 2, 3, 4)

    if in_season:
        logging.info("In basketball season (month=%d), proceeding with scrape", month)
    else:
        logging.info("Off-season (month=%d), skipping scrape", month)

    return in_season


def get_scrape_date(**context) -> str:
    """
    Get the date to scrape (yesterday in UTC).

    Always uses the actual current UTC date minus 1 day to ensure we're
    scraping real data that exists, regardless of how the DAG was triggered.

    Returns date in YYYYMMDD format.
    """
    import logging
    from datetime import datetime, timezone

    # Always use actual yesterday's date (UTC) to ensure we scrape real data
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    scrape_date = yesterday.strftime("%Y%m%d")

    logging.info("Scrape date: %s (yesterday UTC)", scrape_date)
    return scrape_date


def get_season_from_date(date_str: str) -> str:
    """
    Determine the season year from a date.

    College basketball seasons span Nov-Apr, so:
    - Nov-Dec dates belong to next calendar year's season
    - Jan-Apr dates belong to current calendar year's season

    Example:
        20241115 -> "2025" (Nov 2024 is part of 2025 season)
        20250215 -> "2025" (Feb 2025 is part of 2025 season)
    """
    year = int(date_str[:4])
    month = int(date_str[4:6])

    if month >= 11:
        return str(year + 1)
    return str(year)


def scrape_league(league: str, **context) -> dict:
    """
    Scrape ESPN data for a single league for yesterday's date.

    Uses get_missing() which is idempotent - safe to re-run if data
    already exists in cache.

    Args:
        league: 'mens-college-basketball' or 'womens-college-basketball'

    Returns:
        dict with scrape results
    """
    import logging

    from espn_scraper import get_all

    scrape_date = get_scrape_date(**context)
    season = get_season_from_date(scrape_date)

    logging.info("Scraping %s for date %s (season %s)", league, scrape_date, season)

    cache_dir = "/opt/airflow/data/raw/espn"

    try:
        get_all(league, scrape_date, cached_path=cache_dir)
        logging.info("Successfully scraped %s for %s", league, scrape_date)
        return {
            "status": "success",
            "league": league,
            "date": scrape_date,
            "season": season,
        }
    except Exception as e:
        logging.error("Failed to scrape %s: %s", league, str(e))
        raise


def scrape_mens(**context) -> dict:
    """Scrape men's college basketball data."""
    return scrape_league("mens-college-basketball", **context)


def scrape_womens(**context) -> dict:
    """Scrape women's college basketball data."""
    return scrape_league("womens-college-basketball", **context)


# DAG default args
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="espn_scraper_daily",
    description="Daily ESPN college basketball scraper for both leagues",
    default_args=default_args,
    # Run at 6 AM UTC daily (games from previous day should be complete)
    schedule="0 6 * * *",
    start_date=datetime(2025, 11, 1),
    catchup=False,
    tags=["espn", "scraper", "basketball"],
    doc_md=__doc__,
) as dag:
    # Check if we're in basketball season (Nov-Apr)
    check_season = ShortCircuitOperator(
        task_id="check_basketball_season",
        python_callable=is_basketball_season,
    )

    # Scrape both leagues (can run in parallel)
    scrape_mens_task = PythonOperator(
        task_id="scrape_mens_college_basketball",
        python_callable=scrape_mens,
    )

    scrape_womens_task = PythonOperator(
        task_id="scrape_womens_college_basketball",
        python_callable=scrape_womens,
    )

    # Task dependencies: check season first, then scrape both leagues in parallel
    check_season >> [scrape_mens_task, scrape_womens_task]
