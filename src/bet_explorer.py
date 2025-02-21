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
from datetime import datetime

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
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-blink-features"])

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to extract stage values (Regular Season & Playoffs)
def get_stage_values(driver, season):
    BASE_URL = f"https://www.betexplorer.com/basketball/usa/ncaa-{season}/results/"
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
    regular_stage, playoffs_stage = get_stage_values(driver, season)
    months = [f"{season.split('-')[0]}-11", f"{season.split('-')[0]}-12", f"{int(season.split('-')[1])}-01",
              f"{int(season.split('-')[1])}-02", f"{int(season.split('-')[1])}-03"]

    urls = []
    for month in months:
        if regular_stage:
            urls.append(f"https://www.betexplorer.com/basketball/usa/ncaa-{season}/results/?stage={regular_stage}&month={month}")
    
    if playoffs_stage:
        urls.append(f"https://www.betexplorer.com/basketball/usa/ncaa-{season}/results/?stage={playoffs_stage}")

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
            team1 = row.xpath("./td[1]/a/span[1]/strong/text() | ./td[1]/a/span[1]/text()")
            team2 = row.xpath("./td[1]/a/span[2]/strong/text() | ./td[1]/a/span[2]/text()")
            result = row.xpath("./td[2]/a/text()")
            odds1 = row.xpath("./td[3]/span/span/span/text() | ./td[3]/text()")
            odds2 = row.xpath("./td[4]/span/span/span/text() | ./td[4]/text()")
            date = row.xpath("./td[5]/text()")

            if team1 and team2 and result and date:
                # Convert date to standardized format
                match_date = datetime.strptime(date[0], "%d.%m.%Y")
                month = match_date.strftime("%B")

                match_data.append({
                    "Season": season,
                    "Month": month,
                    "Date": match_date.strftime("%Y-%m-%d"),
                    "Team1": team1[0],
                    "Team2": team2[0],
                    "Result": result[0],
                    "Odds1": odds1[0] if odds1 else "N/A",
                    "Odds2": odds2[0] if odds2 else "N/A",
                })

        print(f"Scraped {len(match_data)} games from {url}")
        return match_data
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Main function to scrape multiple seasons and save results
async def scrape_all_seasons():
    start_time = time.time()  # Start timer
    all_matches = []

    seasons = [f"{year}-{year+1}" for year in range(2008, 2024)]  # 2008-2009 to 2023-2024
    driver = get_driver()  # Keep driver open for efficiency

    for season in seasons:
        print(f"\n🔄 Scraping season: {season}...\n")
        urls = build_urls(driver, season)

        async with aiohttp.ClientSession() as session:
            tasks = [parse_page(driver, url, season) for url in urls]
            results = await asyncio.gather(*tasks)

        # Flatten the results list and add to all_matches
        for result in results:
            all_matches.extend(result)

    driver.quit()  # Close Selenium browser

    end_time = time.time()  # End timer

    # Convert to DataFrame
    df = pd.DataFrame(all_matches, columns=["Season", "Month", "Date", "Team1", "Team2", "Result", "Odds1", "Odds2"])

    # Save to CSV
    df.to_csv("ncaam_betexplorer_odds.csv", index=False)

    print("\n=== ✅ Scraping Complete ✅ ===")
    print(f"Total Games Scraped: {len(all_matches)}")
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    print(f"CSV Saved: ncaam_betexplorer_odds.csv")

    return df  # Return DataFrame for further analysis if needed

# Run the scraper for all seasons
df_all = asyncio.run(scrape_all_seasons())
