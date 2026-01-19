"""
Command-line interface for ESPN parser.

Provides commands to:
- Parse all data for a league/season
- Parse specific data types (events, games, boxscores, playbyplay)
- List cached raw data
"""

import click

from espn_parser.leagues import get_available_seasons, get_leagues
from espn_parser.parser import (
    parse_all,
    parse_boxscores,
    parse_events,
    parse_games,
    parse_playbyplay,
)
from espn_parser.reader import count_files, list_cached_seasons


@click.group()
@click.version_option(version="0.1.0", prog_name="espn-parser")
def cli():
    """
    ESPN Basketball Parser - Parse cached ESPN data into parquet files.

    This tool reads raw ESPN JSON data from data/raw/espn and outputs
    structured parquet files to data/parsed/espn.
    """
    pass


def parse_leagues(league_arg):
    """Parse league argument, expanding 'both' to both leagues."""
    if league_arg == "both":
        return ["mens-college-basketball", "womens-college-basketball"]
    return [league_arg]


def parse_seasons(season_arg, league):
    """
    Parse season argument, supporting comma-separated values and year ranges.

    Examples:
        "2024" -> ["2024"]
        "2023,2024,2025" -> ["2023", "2024", "2025"]
        "2020-2024" -> ["2020", "2021", "2022", "2023", "2024"]
        "all" -> all available seasons
    """
    if season_arg == "all":
        return get_available_seasons(league)

    # Check for comma-separated values
    if "," in season_arg:
        return [s.strip() for s in season_arg.split(",")]

    # Check for year range (4 digits - 4 digits)
    if "-" in season_arg:
        parts = season_arg.split("-")
        if len(parts) == 2 and len(parts[0]) == 4 and len(parts[1]) == 4:
            try:
                start_year = int(parts[0])
                end_year = int(parts[1])
                return [str(year) for year in range(start_year, end_year + 1)]
            except ValueError:
                pass  # Not a year range

    # Single season
    return [season_arg]


@cli.command("parse-all")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball", "both"]),
    required=True,
    help="League to parse ('both' for men's and women's)",
)
@click.option(
    "--season",
    "-s",
    type=str,
    help=(
        'Season year (e.g., "2024"), multiple seasons (e.g., "2023,2024,2025" or "2020-2024"), '
        'or "all" for all available seasons'
    ),
    required=True,
)
@click.option(
    "--raw-dir",
    "-r",
    type=click.Path(),
    default="data/raw/espn",
    help="Directory containing raw ESPN JSON files (default: data/raw/espn)",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="data/parsed/espn",
    help="Directory to write parquet files (default: data/parsed/espn)",
)
def parse_all_cmd(league, season, raw_dir, output_dir):
    """
    Parse all ESPN data (events, games, teams, players, boxscores, playbyplay).

    This command will read raw JSON files and output structured parquet files
    for all data types.

    Examples:

        # Parse entire season
        espn-parser parse-all -l mens-college-basketball -s 2024

        # Parse multiple seasons
        espn-parser parse-all -l mens-college-basketball -s 2020-2024

        # Parse both leagues
        espn-parser parse-all -l both -s 2024

        # Parse all available seasons
        espn-parser parse-all -l mens-college-basketball -s all
    """
    leagues = parse_leagues(league)

    for lg in leagues:
        seasons = parse_seasons(season, lg)
        click.echo(f"League: {lg}")
        click.echo(f"Seasons: {', '.join(seasons)}")
        click.echo(f"Raw directory: {raw_dir}")
        click.echo(f"Output directory: {output_dir}")

        for sn in seasons:
            click.echo(f"\n{'='*60}")
            click.echo(f"Parsing: {lg} - {sn}")
            click.echo("=" * 60)
            try:
                parse_all(lg, sn, raw_dir, output_dir)
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)

    click.echo("\nDone!")


@cli.command("parse-events")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball", "both"]),
    required=True,
    help="League to parse",
)
@click.option(
    "--season",
    "-s",
    type=str,
    required=True,
    help='Season year (e.g., "2024") or range (e.g., "2020-2024")',
)
@click.option(
    "--raw-dir",
    "-r",
    type=click.Path(),
    default="data/raw/espn",
    help="Directory containing raw ESPN JSON files",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="data/parsed/espn",
    help="Directory to write parquet files",
)
def parse_events_cmd(league, season, raw_dir, output_dir):
    """
    Parse schedule events (also extracts teams and venues).

    Output files: events.parquet, teams.parquet, venues.parquet
    """
    leagues = parse_leagues(league)

    for lg in leagues:
        seasons = parse_seasons(season, lg)
        for sn in seasons:
            click.echo(f"Parsing events: {lg} - {sn}")
            try:
                parse_events(lg, sn, raw_dir, output_dir)
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)

    click.echo("\nDone!")


@cli.command("parse-games")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball", "both"]),
    required=True,
    help="League to parse",
)
@click.option(
    "--season",
    "-s",
    type=str,
    required=True,
    help='Season year (e.g., "2024") or range (e.g., "2020-2024")',
)
@click.option(
    "--raw-dir",
    "-r",
    type=click.Path(),
    default="data/raw/espn",
    help="Directory containing raw ESPN JSON files",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="data/parsed/espn",
    help="Directory to write parquet files",
)
def parse_games_cmd(league, season, raw_dir, output_dir):
    """
    Parse game data.

    Output files: games.parquet, teams.parquet
    """
    leagues = parse_leagues(league)

    for lg in leagues:
        seasons = parse_seasons(season, lg)
        for sn in seasons:
            click.echo(f"Parsing games: {lg} - {sn}")
            try:
                parse_games(lg, sn, raw_dir, output_dir)
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)

    click.echo("\nDone!")


@cli.command("parse-boxscores")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball", "both"]),
    required=True,
    help="League to parse",
)
@click.option(
    "--season",
    "-s",
    type=str,
    required=True,
    help='Season year (e.g., "2024") or range (e.g., "2020-2024")',
)
@click.option(
    "--raw-dir",
    "-r",
    type=click.Path(),
    default="data/raw/espn",
    help="Directory containing raw ESPN JSON files",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="data/parsed/espn",
    help="Directory to write parquet files",
)
def parse_boxscores_cmd(league, season, raw_dir, output_dir):
    """
    Parse boxscore statistics (also extracts players).

    Output files: boxscores.parquet, players.parquet
    """
    leagues = parse_leagues(league)

    for lg in leagues:
        seasons = parse_seasons(season, lg)
        for sn in seasons:
            click.echo(f"Parsing boxscores: {lg} - {sn}")
            try:
                parse_boxscores(lg, sn, raw_dir, output_dir)
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)

    click.echo("\nDone!")


@cli.command("parse-playbyplay")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball", "both"]),
    required=True,
    help="League to parse",
)
@click.option(
    "--season",
    "-s",
    type=str,
    required=True,
    help='Season year (e.g., "2024") or range (e.g., "2020-2024")',
)
@click.option(
    "--raw-dir",
    "-r",
    type=click.Path(),
    default="data/raw/espn",
    help="Directory containing raw ESPN JSON files",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default="data/parsed/espn",
    help="Directory to write parquet files",
)
def parse_playbyplay_cmd(league, season, raw_dir, output_dir):
    """
    Parse play-by-play data.

    Output file: playbyplay.parquet
    """
    leagues = parse_leagues(league)

    for lg in leagues:
        seasons = parse_seasons(season, lg)
        for sn in seasons:
            click.echo(f"Parsing play-by-play: {lg} - {sn}")
            try:
                parse_playbyplay(lg, sn, raw_dir, output_dir)
            except ValueError as e:
                click.echo(f"Error: {e}", err=True)

    click.echo("\nDone!")


@cli.command("list-cached")
@click.option(
    "--league",
    "-l",
    type=click.Choice(["mens-college-basketball", "womens-college-basketball", "both"]),
    default="both",
    help="League to list cached data for",
)
@click.option(
    "--raw-dir",
    "-r",
    type=click.Path(),
    default="data/raw/espn",
    help="Directory containing raw ESPN JSON files",
)
def list_cached_cmd(league, raw_dir):
    """
    List available cached raw data.

    Shows seasons and file counts for each data type.
    """
    leagues = parse_leagues(league)

    for lg in leagues:
        click.echo(f"\n{lg}")
        click.echo("=" * len(lg))

        seasons = list_cached_seasons(lg, raw_dir)
        if not seasons:
            click.echo("  No cached data found")
            continue

        for sn in seasons:
            schedule_count = count_files(lg, sn, "schedule", raw_dir)
            game_count = count_files(lg, sn, "game", raw_dir)
            boxscore_count = count_files(lg, sn, "boxscore", raw_dir)
            playbyplay_count = count_files(lg, sn, "playbyplay", raw_dir)

            click.echo(
                f"  {sn}: {schedule_count} schedules, {game_count} games, "
                f"{boxscore_count} boxscores, {playbyplay_count} playbyplay"
            )


@cli.command("list-leagues")
def list_leagues_cmd():
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
def list_seasons_cmd(league):
    """List all available seasons for a league."""
    seasons = get_available_seasons(league)
    click.echo(f"Available seasons for {league}:")
    click.echo(f"  {seasons[0]} - {seasons[-1]} ({len(seasons)} seasons)")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
