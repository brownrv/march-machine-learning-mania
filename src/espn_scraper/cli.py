"""
Command-line interface for ESPN scraper.

Provides commands to:
- Fetch all data for a league/season/date
- Check cache and fetch missing data
- List supported leagues and seasons
"""

import click

from .leagues import get_available_seasons, get_leagues
from .scraper import get_all, get_missing


@click.group()
@click.version_option(version="0.1.0", prog_name="espn-scraper")
def cli():
    """
    ESPN Basketball Scraper - Fetch NCAA basketball data from ESPN's JSON API.

    This tool scrapes schedule, game, boxscore, and play-by-play data
    for college basketball games and caches them locally.
    """
    pass


@cli.command("get-all")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball"]),
    required=True,
    help="League to scrape",
)
@click.option(
    "--season",
    "-s",
    type=str,
    help=(
        'Season year (e.g., "2024"), date (e.g., "20240315"), '
        'or date range (e.g., "20240101-20240331")'
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

        # Fetch single date
        espn-scraper get-all -l womens-college-basketball -s 20240315

        # Fetch date range
        espn-scraper get-all -l mens-college-basketball -s 20240101-20240331
    """
    click.echo(f"Fetching all data for {league} - {season}")
    click.echo(f"Cache directory: {cache_dir}")
    get_all(league, season, cache_dir)
    click.echo("✓ Done!")


@cli.command("get-missing")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball"]),
    required=True,
    help="League to check",
)
@click.option(
    "--season",
    "-s",
    type=str,
    help=(
        'Season year (e.g., "2024"), date (e.g., "20240315"), '
        'or date range (e.g., "20240101-20240331")'
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

        # Check specific date
        espn-scraper get-missing -l womens-college-basketball -s 20240315
    """
    click.echo(f"Checking cache for {league} - {season}")
    click.echo(f"Cache directory: {cache_dir}")
    get_missing(league, season, cache_dir)
    click.echo("✓ Done!")


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
