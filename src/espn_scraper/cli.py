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
