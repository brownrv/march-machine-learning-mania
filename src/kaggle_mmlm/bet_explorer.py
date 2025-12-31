import aiohttp
import asyncio
import time
import pandas as pd
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta


# Initialize Selenium WebDriver (Keep it Open for Efficiency)
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Suppress unnecessary logs
    options.add_argument("--log-level=3")  # Suppresses warnings/errors
    options.add_argument("--disable-logging")
    options.add_argument("--silent")  # Mutes most logs
    options.add_argument("--remote-debugging-port=0")  # Prevents DevTools messages
    options.add_experimental_option(
        "excludeSwitches", ["enable-logging", "enable-blink-features"]
    )

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )


# Function to extract stage values (Regular Season & Playoffs)
def get_stage_values(driver, season):
    # BASE_URL = f"https://www.betexplorer.com/basketball/usa/ncaa-{season}/results/"
    BASE_URL = (
        f"https://www.betexplorer.com/basketball/usa/ncaa-women-{season}/results/"
    )
    driver.get(BASE_URL)
    time.sleep(2)  # Allow JavaScript to load

    stages = {}
    tabs = driver.find_elements(By.CSS_SELECTOR, "ul.list-tabs li a")

    for tab in tabs:
        title = tab.get_attribute("title").lower()
        stage_param = tab.get_attribute("href").split("=")[-1]
        if "play" in title:
            stages["playoffs"] = stage_param
        elif "main" in title or "regular" in title:
            stages["regular_season"] = stage_param

    return stages.get("regular_season"), stages.get("playoffs")


# Function to build URLs dynamically
def build_urls(driver, season):
    """Builds a list of URLs for scraping, ensuring no future months are included."""
    regular_stage, playoffs_stage = get_stage_values(driver, season)

    # Generate months list dynamically
    months = [
        f"{season.split('-')[0]}-11",
        f"{season.split('-')[0]}-12",
        f"{int(season.split('-')[1])}-01",
        f"{int(season.split('-')[1])}-02",
        f"{int(season.split('-')[1])}-03",
    ]

    # Get current year and month
    current_year, current_month = datetime.now().year, datetime.now().month

    # Filter out future months
    valid_months = [
        month
        for month in months
        if int(month.split("-")[0]) < current_year
        or (
            int(month.split("-")[0]) == current_year
            and int(month.split("-")[1]) <= current_month
        )
    ]

    urls = []

    if regular_stage:  # Use regular season stage if available
        for month in valid_months:
            # urls.append(f"https://www.betexplorer.com/basketball/usa/ncaa-{season}/results/?stage={regular_stage}&month={month}")
            urls.append(
                f"https://www.betexplorer.com/basketball/usa/ncaa-women-{season}/results/?stage={regular_stage}&month={month}"
            )
    else:  # If no stage, use month-based URLs
        for month in valid_months:
            # urls.append(f"https://www.betexplorer.com/basketball/usa/ncaa-{season}/results/?month={month}")
            urls.append(
                f"https://www.betexplorer.com/basketball/usa/ncaa-women-{season}/results/?month={month}"
            )

    if playoffs_stage:  # Include playoffs if available
        # urls.append(f"https://www.betexplorer.com/basketball/usa/ncaa-{season}/results/?stage={playoffs_stage}")
        urls.append(
            f"https://www.betexplorer.com/basketball/usa/ncaa-women-{season}/results/?stage={playoffs_stage}"
        )

    return urls


# Function to build URLs dynamically
def build_tournament_urls(driver):
    """Builds a list of URLs for scraping upcoming tournament games."""

    urls = []
    urls.append(f"https://www.betexplorer.com/basketball/usa/ncaa")
    # urls.append(f"https://www.betexplorer.com/basketball/usa/ncaa-women")

    return urls


# Function to fetch a fully rendered webpage using Selenium
def fetch_page_with_selenium(driver, url):
    driver.get(url)

    try:
        # Wait until the match table is fully loaded (timeout after 10 seconds)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table/tbody/tr[td]"))
        )
    except Exception as e:
        print(f"Warning: Page {url} may not have fully loaded. {e}")

    return driver.page_source  # Get fully rendered HTML


def parse_match_date(date_str):
    """Parses match date, handling missing year and 'Yesterday' cases."""
    try:
        if date_str.lower() == "yesterday":
            # Handle "Yesterday" case
            match_date = datetime.now() - timedelta(days=1)
        else:
            try:
                # Try parsing with full date format (e.g., "10.03.2023")
                match_date = datetime.strptime(date_str, "%d.%m.%Y")
            except ValueError:
                # If the year is missing (e.g., "10.03"), append the current year
                current_year = datetime.now().year
                date_with_year = f"{date_str}{current_year}"
                match_date = datetime.strptime(date_with_year, "%d.%m.%Y")

    except ValueError:
        print(f"⚠️ Warning: Unable to parse date '{date_str}', returning None")
        return None

    return match_date


# Function to parse a single page and extract match data
async def parse_page(driver, url, season):
    try:
        page_content = fetch_page_with_selenium(driver, url)

        # Check if response is empty or invalid
        if not page_content.strip():
            print(f"Skipping {url} - Empty document")
            return []

        tree = html.fromstring(page_content)

        # Extract only rows that contain <td> (ignoring <th> header rows)
        rows = tree.xpath("//table/tbody/tr[td]")

        match_data = []
        for row in rows:
            team1 = row.xpath(
                "./td[1]/a/span[1]/strong/text() | ./td[1]/a/span[1]/text()"
            )
            team2 = row.xpath(
                "./td[1]/a/span[2]/strong/text() | ./td[1]/a/span[2]/text()"
            )
            result = row.xpath("./td[2]/a/text()")
            odds1 = row.xpath("./td[3]/span/span/span/text() | ./td[3]/text()")
            odds2 = row.xpath("./td[4]/span/span/span/text() | ./td[4]/text()")
            date = row.xpath("./td[5]/text()")

            if team1 and team2 and result and date:
                # Convert date to standardized format
                # match_date = datetime.strptime(date[0], "%d.%m.%Y")
                match_date = parse_match_date(date[0])
                month = match_date.strftime("%B")

                match_data.append(
                    {
                        "Season": season,
                        "Month": month,
                        "Date": match_date.strftime("%Y-%m-%d"),
                        "Team1": team1[0],
                        "Team2": team2[0],
                        "Result": result[0],
                        "Odds1": odds1[0] if odds1 else "N/A",
                        "Odds2": odds2[0] if odds2 else "N/A",
                    }
                )

        print(f"Scraped {len(match_data)} games from {url}")
        return match_data
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []


# Function to parse a single page and extract match data
# async def parse_summary_page(driver, url, season):
#     try:
#         page_content = fetch_page_with_selenium(driver, url)

#         # Check if response is empty or invalid
#         if not page_content.strip():
#             print(f"Skipping {url} - Empty document")
#             return []

#         tree = html.fromstring(page_content)

#         # Extract only rows that contain <td> (ignoring <th> header rows)
#         rows = tree.xpath("//table/tbody/tr[td]")

#         match_data = []
#         for row in rows:
#             team1 = row.xpath("./td[1]/a/span[1]/strong/text() | ./td[1]/a/span[1]/text()")
#             team2 = row.xpath("./td[1]/a/span[2]/strong/text() | ./td[1]/a/span[2]/text()")
#             odds1 = row.xpath("./td[3]/span/span/span/text() | ./td[3]/text()")
#             odds2 = row.xpath("./td[4]/span/span/span/text() | ./td[4]/text()")
#             date = row.xpath("./td[5]/text()")

#             if team1 and team2 and date:
#                 match_data.append({
#                     "Season": season,
#                     "Date": date,
#                     "Team1": team1[0],
#                     "Team2": team2[0],
#                     "Odds1": odds1[0] if odds1 else "N/A",
#                     "Odds2": odds2[0] if odds2 else "N/A",
#                 })

#         print(f"Scraped {len(match_data)} games from {url}")
#         return match_data
#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
#         return []

from lxml import html
import time
import asyncio


async def parse_summary_page(driver, url, season):
    """Scrapes match summary page for team names, odds, and dates."""
    try:
        # Fetch page content
        page_content = fetch_page_with_selenium(driver, url)

        # Check if response is empty or invalid
        if not page_content.strip():
            print(f"Skipping {url} - Empty document")
            return []

        tree = html.fromstring(page_content)

        # Extract only rows that contain <td> (ignoring <th> header rows)
        rows = tree.xpath(
            "/html/body/div[2]/div[3]/div/div/div[1]/section/div[3]/div/table/tbody/tr"
        )

        match_data = []
        for index, row in enumerate(rows, start=1):
            try:
                # Use dynamic XPath to adjust row index
                team1_xpath = f"/html/body/div[2]/div[3]/div/div/div[1]/section/div[3]/div/table/tbody/tr[{index}]/td[2]/a/span[1]/text()"
                team2_xpath = f"/html/body/div[2]/div[3]/div/div/div[1]/section/div[3]/div/table/tbody/tr[{index}]/td[2]/a/span[2]/text()"
                odds1_xpath = f"/html/body/div[2]/div[3]/div/div/div[1]/section/div[3]/div/table/tbody/tr[{index}]/td[6]/button/text()"
                odds2_xpath = f"/html/body/div[2]/div[3]/div/div/div[1]/section/div[3]/div/table/tbody/tr[{index}]/td[7]/button/text()"
                date_xpath = f"/html/body/div[2]/div[3]/div/div/div[1]/section/div[3]/div/table/tbody/tr[{index}]/td[8]/text()"

                # Extract values
                team1 = tree.xpath(team1_xpath)
                team2 = tree.xpath(team2_xpath)
                odds1 = tree.xpath(odds1_xpath)
                odds2 = tree.xpath(odds2_xpath)
                date = tree.xpath(date_xpath)

                if team1 and team2 and date:
                    match_data.append(
                        {
                            "Season": season,
                            "Date": date[0].strip() if date else "N/A",
                            "Team1": team1[0].strip() if team1 else "N/A",
                            "Team2": team2[0].strip() if team2 else "N/A",
                            "Odds1": odds1[0].strip() if odds1 else "N/A",
                            "Odds2": odds2[0].strip() if odds2 else "N/A",
                        }
                    )

            except Exception as row_error:
                print(f"⚠️ Skipping row {index} due to error: {row_error}")

        print(f"✅ Scraped {len(match_data)} games from {url}")
        return match_data

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return []


# Main function to scrape multiple seasons and save results
async def scrape_all_seasons():
    start_time = time.time()  # Start timer
    all_matches = []

    # seasons = [f"{year}-{year+1}" for year in range(2008, 2024)]  # 2008-2009 to 2023-2024
    seasons = ["2024-2025"]  # 2024-2025
    driver = get_driver()  # Keep driver open for efficiency

    for season in seasons:
        print(f"\n🔄 Scraping season: {season}...\n")
        # urls = build_urls(driver, season)
        urls = build_tournament_urls(driver)

        async with aiohttp.ClientSession() as session:
            # tasks = [parse_page(driver, url, season) for url in urls]
            tasks = [parse_summary_page(driver, url, season) for url in urls]
            results = await asyncio.gather(*tasks)

        # Flatten the results list and add to all_matches
        for result in results:
            all_matches.extend(result)

    driver.quit()  # Close Selenium browser

    end_time = time.time()  # End timer

    # Convert to DataFrame
    # df = pd.DataFrame(all_matches, columns=["Season", "Month", "Date", "Team1", "Team2", "Result", "Odds1", "Odds2"])
    df = pd.DataFrame(
        all_matches, columns=["Season", "Date", "Team1", "Team2", "Odds1", "Odds2"]
    )

    # Save to CSV
    # df.to_csv("ncaam_betexplorer_odds.csv", index=False)
    # df.to_csv("ncaam_betexplorer_odds_2024-2025.csv", index=False)
    df.to_csv("ncaam_betexplorer_odds_20250319.csv", index=False)

    print("\n=== ✅ Scraping Complete ✅ ===")
    print(f"Total Games Scraped: {len(all_matches)}")
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    # print(f"CSV Saved: ncaam_betexplorer_odds.csv")
    print(f"CSV Saved: ncaam_betexplorer_odds_20250319.csv")

    return df  # Return DataFrame for further analysis if needed


# Function to scrape the current season and update CSV
# async def scrape_and_update_current_season():
#     """Scrapes the current NCAA season and updates `ncaam_betexplorer_odds.csv` with new and changed records."""
#     start_time = time.time()  # Start timer
#     all_matches = []

#     # Determine the current season
#     current_year = datetime.now().year
#     current_season = f"{current_year-1}-{current_year}" if datetime.now().month <= 10 else f"{current_year}-{current_year+1}"

#     print(f"\n🔄 Scraping current season: {current_season}...\n")

#     driver = get_driver()
#     urls = build_urls(driver, current_season)

#     async with aiohttp.ClientSession() as session:
#         tasks = [parse_page(driver, url, current_season) for url in urls]
#         results = await asyncio.gather(*tasks)

#     # Flatten results list and add to matches
#     for result in results:
#         all_matches.extend(result)

#     driver.quit()  # Close Selenium

#     # Convert new scraped data to DataFrame
#     df_new = pd.DataFrame(all_matches, columns=["Season", "Month", "Date", "Team1", "Team2", "Result", "Odds1", "Odds2"])

#     # Load existing data
#     try:
#         df_existing = pd.read_csv("ncaam_betexplorer_odds.csv", dtype=str)
#     except FileNotFoundError:
#         print("No existing file found. Creating a new one.")
#         df_new.to_csv("ncaam_betexplorer_odds.csv", index=False)
#         print(f"✅ CSV Created: ncaam_betexplorer_odds.csv")
#         return df_new

#     # Ensure Date column is in consistent format
#     df_existing["Date"] = pd.to_datetime(df_existing["Date"])
#     df_new["Date"] = pd.to_datetime(df_new["Date"])

#     # Merge DataFrames on primary key (Team1, Team2, Date)
#     df_combined = df_existing.merge(df_new, on=["Team1", "Team2", "Date"], how="outer", suffixes=("_old", "_new"))

#     # Identify new rows (not in existing data)
#     new_rows = df_combined[df_combined["Season_old"].isna()][["Season_new", "Month_new", "Date", "Team1", "Team2", "Result_new", "Odds1_new", "Odds2_new"]]
#     new_rows.columns = ["Season", "Month", "Date", "Team1", "Team2", "Result", "Odds1", "Odds2"]

#     # Identify updated rows (Result, Odds1, or Odds2 changed)
#     updated_rows = df_combined[
#         (df_combined["Result_old"] != df_combined["Result_new"]) |
#         (df_combined["Odds1_old"] != df_combined["Odds1_new"]) |
#         (df_combined["Odds2_old"] != df_combined["Odds2_new"])
#     ][["Season_new", "Month_new", "Date", "Team1", "Team2", "Result_new", "Odds1_new", "Odds2_new"]]
#     updated_rows.columns = ["Season", "Month", "Date", "Team1", "Team2", "Result", "Odds1", "Odds2"]

#     # Update existing dataset
#     df_updated = pd.concat([df_existing, new_rows, updated_rows]).drop_duplicates(subset=["Team1", "Team2", "Date"], keep="last")

#     # Save updated dataset
#     df_updated.to_csv("ncaam_betexplorer_odds.csv", index=False)

#     end_time = time.time()  # End timer

#     print("\n=== ✅ Scraping & Update Complete ✅ ===")
#     print(f"🔄 New rows added: {len(new_rows)}")
#     print(f"🔄 Existing rows updated: {len(updated_rows)}")
#     print(f"📊 Total records in updated file: {len(df_updated)}")
#     print(f"⏳ Total Time: {end_time - start_time:.2f} seconds")

#     return df_updated

# Run the scraper for all seasons
df_all = asyncio.run(scrape_all_seasons())

# Run the scraper for current seasons
# df_current = asyncio.run(scrape_and_update_current_season())
