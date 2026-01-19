"""
Command-line interface for ESPN scraper.

Provides commands to:
- Fetch all data for a league/season/date
- Check cache and fetch missing data
- List supported leagues and seasons
"""

import logging
import os
import sys

import click

from .leagues import get_available_seasons, get_leagues
from .scraper import get_all, get_missing

# Default log directory
LOG_DIR = "logs"


def setup_logging(verbose: int, log_file: str | None = None) -> None:
    """
    Configure logging based on verbosity level.

    Args:
        verbose: Verbosity level (0=WARNING, 1=INFO, 2+=DEBUG)
        log_file: Optional path to log file. If provided, logs are written to file
                  at INFO level (or higher if verbose) in addition to stderr.
    """
    if verbose == 0:
        level = logging.WARNING
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Get our package's logger
    logger = logging.getLogger("espn_scraper")
    logger.setLevel(logging.DEBUG)  # Capture all, let handlers filter

    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        # Ensure logs directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # File always gets at least INFO level for review
        file_level = min(level, logging.INFO)
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        click.echo(f"Logging to: {log_file}")


@click.group()
@click.version_option(version="0.1.0", prog_name="espn-scraper")
@click.option(
    "-v", "--verbose",
    count=True,
    help="Increase verbosity (-v for INFO, -vv for DEBUG)",
)
@click.option(
    "--log-file",
    type=click.Path(),
    default=os.path.join(LOG_DIR, "espn-scraper.log"),
    help=f"Write logs to file (default: {LOG_DIR}/espn-scraper.log)",
)
@click.pass_context
def cli(ctx, verbose, log_file):
    """
    ESPN Basketball Scraper - Fetch NCAA basketball data from ESPN's JSON API.

    This tool scrapes schedule, game, boxscore, and play-by-play data
    for college basketball games and caches them locally.

    Use -v for INFO level logging (shows OK/SKIPPED for each URL).
    Use -vv for DEBUG level logging (shows all fetch attempts).
    Use --log-file to save logs for later review.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["log_file"] = log_file
    setup_logging(verbose, log_file)


def parse_leagues(league_arg):
    """Parse league argument, expanding 'both' to both leagues."""
    if league_arg == "both":
        return ["mens-college-basketball", "womens-college-basketball"]
    return [league_arg]


def parse_seasons(season_arg):
    """
    Parse season argument, supporting comma-separated values and year ranges.

    Examples:
        "2024" -> ["2024"]
        "2023,2024,2025" -> ["2023", "2024", "2025"]
        "2020-2024" -> ["2020", "2021", "2022", "2023", "2024"]
        "20241104" -> ["20241104"] (single date, passed through)
        "20241101-20241231" -> ["20241101-20241231"] (date range, passed through)
    """
    # Check for comma-separated values
    if "," in season_arg:
        return [s.strip() for s in season_arg.split(",")]

    # Check for year range (4 digits - 4 digits, not date range which is 8-8)
    if "-" in season_arg:
        parts = season_arg.split("-")
        if len(parts) == 2 and len(parts[0]) == 4 and len(parts[1]) == 4:
            try:
                start_year = int(parts[0])
                end_year = int(parts[1])
                return [str(year) for year in range(start_year, end_year + 1)]
            except ValueError:
                pass  # Not a year range, treat as date range

    # Single value (season year, single date, or date range)
    return [season_arg]


@cli.command("get-all")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball", "both"]),
    required=True,
    help="League to scrape ('both' for men's and women's)",
)
@click.option(
    "--season",
    "--date",
    "--range",
    "-s",
    type=str,
    help=(
        'Season year (e.g., "2024"), multiple seasons (e.g., "2023,2024,2025" or "2020-2024"), '
        'date (e.g., "20240315"), or date range (e.g., "20240101-20240331")'
    ),
    required=True,
)
@click.option(
    "--cache-dir",
    "-c",
    type=click.Path(),
    default="cached_data",
    help="Directory to cache JSON files (default: cached_data)",
)
def get_all_cmd(league, season, cache_dir):
    """
    Fetch all ESPN data (schedule + games) for a league/season/date.

    This command will:
    1. Fetch schedule data for the specified league and season/date
    2. Extract game IDs from each schedule
    3. Fetch game, boxscore, and play-by-play data for each game
    4. Cache all data to the specified directory

    Examples:

        # Fetch entire season
        espn-scraper get-all -l mens-college-basketball -s 2024

        # Fetch multiple seasons
        espn-scraper get-all -l mens-college-basketball -s 2020-2024

        # Fetch both leagues for a date
        espn-scraper get-all -l both -s 20240315

        # Fetch single date
        espn-scraper get-all -l womens-college-basketball -s 20240315

        # Fetch date range
        espn-scraper get-all -l mens-college-basketball -s 20240101-20240331
    """
    leagues = parse_leagues(league)
    seasons = parse_seasons(season)

    click.echo(f"Leagues: {', '.join(leagues)}")
    click.echo(f"Seasons/dates: {', '.join(seasons)}")
    click.echo(f"Cache directory: {cache_dir}")

    for lg in leagues:
        for sn in seasons:
            click.echo(f"\n{'='*60}")
            click.echo(f"Fetching: {lg} - {sn}")
            click.echo('='*60)
            get_all(lg, sn, cache_dir)

    click.echo("\n✓ All done!")


@cli.command("get-missing")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball", "both"]),
    required=True,
    help="League to check ('both' for men's and women's)",
)
@click.option(
    "--season",
    "--date",
    "--range",
    "-s",
    type=str,
    help=(
        'Season year (e.g., "2024"), multiple seasons (e.g., "2023,2024,2025" or "2020-2024"), '
        'date (e.g., "20240315"), or date range (e.g., "20240101-20240331")'
    ),
    required=True,
)
@click.option(
    "--cache-dir",
    "-c",
    type=click.Path(),
    default="cached_data",
    help="Directory where JSON files are cached (default: cached_data)",
)
def get_missing_cmd(league, season, cache_dir):
    """
    Check cache for missing data and fetch it.

    This command will:
    1. Check if schedules are cached
    2. For cached schedules, check if all games are cached
    3. Identify missing data
    4. Fetch only the missing data

    Useful for:
    - Resuming interrupted scraping sessions
    - Fetching newly added games for current season
    - Validating cache completeness

    Examples:

        # Check and fill gaps for a season
        espn-scraper get-missing -l mens-college-basketball -s 2024

        # Check multiple seasons
        espn-scraper get-missing -l both -s 2020-2024

        # Check specific date
        espn-scraper get-missing -l womens-college-basketball -s 20240315
    """
    leagues = parse_leagues(league)
    seasons = parse_seasons(season)

    click.echo(f"Leagues: {', '.join(leagues)}")
    click.echo(f"Seasons/dates: {', '.join(seasons)}")
    click.echo(f"Cache directory: {cache_dir}")

    for lg in leagues:
        for sn in seasons:
            click.echo(f"\n{'='*60}")
            click.echo(f"Checking: {lg} - {sn}")
            click.echo('='*60)
            get_missing(lg, sn, cache_dir)

    click.echo("\n✓ All done!")


@cli.command("list-leagues")
def list_leagues():
    """List all supported leagues."""
    click.echo("Supported leagues:")
    for league in get_leagues():
        click.echo(f"  - {league}")


@cli.command("list-seasons")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball"]),
    required=True,
    help="League to list seasons for",
)
def list_seasons(league):
    """List all available seasons for a league."""
    seasons = get_available_seasons(league)
    click.echo(f"Available seasons for {league}:")
    click.echo(f"  {seasons[0]} - {seasons[-1]} ({len(seasons)} seasons)")
    if len(seasons) <= 20:
        for season in seasons:
            click.echo(f"  - {season}")
    else:
        click.echo("  (showing first 5 and last 5)")
        for season in seasons[:5]:
            click.echo(f"  - {season}")
        click.echo("  ...")
        for season in seasons[-5:]:
            click.echo(f"  - {season}")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
