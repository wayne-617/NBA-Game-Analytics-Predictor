import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import time
import asyncio
import sys

SEASONS = list(range(2016,2024))
DATA_DIR = "data"
SCHEDULES_DIR = os.path.join(DATA_DIR, "schedules")
SCORES_DIR = os.path.join(DATA_DIR, "scores")

# grab specified html give the url and selector
async def get_html(url, selector, sleep = 5, retries = 3):
    html = None
    for i in range(1, retries + 1):
        time.sleep(sleep * i)
        try :
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                print("launched")
                page = await browser.new_page()
                await page.goto(url)
                print(await page.title())
                html = await page.inner_html(selector)
        except PlaywrightTimeout:
            print(f"Timeout error on {url}")
            continue
        else:
            break
    return html
    
# scrape links for the box score tables in that season
async def scrape_season(season):
    url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"
    html = await fetch_data(url)

    soup = BeautifulSoup(html)
    links = soup.find_all("a") # get anchor tags
    href = [l.get("href") for l in links] # parse links
    schedules_pages = [f"https://basketball-reference.com{l}" for l in href] # transform links into full urls

    for url in schedules_pages:
        path = os.path.join(SCHEDULES_DIR, url.split("/")[-1]) # create path to file based off url
        if os.path.exists(path):
            print(f"{path} already exists")
            continue # continue if page is already scraped

        html = await get_html(url, "#all_schedule") # grab html for schedule table
        if html is not None:
            with open(path, "w+") as f:
                f.write(html)

        else:
            print(f"{html} is None")

# scrape a schedule file and save all the box scores into scores
async def scrape_game(schedules_file):
    with open(schedules_file, 'r') as f:
        html = f.read()

    soup = BeautifulSoup(html)
    links = soup.find_all("a")
    hrefs = [l.get("href") for l in links]
    box_scores = [l for l in hrefs if l and "boxscore" in l and ".html" in l]
    box_scores = [f"https://www.basketball-reference.com{l}" for l in box_scores]

    for url in box_scores:
        save_path = os.path.join(SCORES_DIR, url.split("/")[-1])
        if os.path.exists(save_path):
            print(f"{save_path} already exists")
            continue

        html = await get_html(url, "#content")
        if not html:
            continue
        with open(save_path, "w+", encoding='utf-8') as f:
            f.write(html)


async def fetch_data(url):
    html = await get_html(url, "#content .filter")
    print(html)
    return html

async def fetch_schedule(season):
    await scrape_season(season)

async def main():
    if len(sys.argv) < 2:
        # scrape season schedules into schedule directory
        await asyncio.gather(*(scrape_season(season) for season in SEASONS))

        # list of all html files in schedule directory
        schedules_files = [f for f in os.listdir(SCHEDULES_DIR) if f.endswith('.html')]

        # scrape games for each html file
        for f in schedules_files:
            filepath = os.path.join(SCHEDULES_DIR, f) # get full file path
            await scrape_game(filepath)

    else:
        command = sys.argv[1]

        if command == "schedules":
            print("Scraping Schedules")

            await asyncio.gather(*(scrape_season(season) for season in SEASONS))

            print("Finished Scraping Schedules")

        elif command == "games":
            print("Scraping Games From Schedules")

            schedules_files = [f for f in os.listdir(SCHEDULES_DIR) if f.endswith('.html')]

            for f in schedules_files:
                filepath = os.path.join(SCHEDULES_DIR, f) # get full file path
                await scrape_game(filepath)
                
            print("Finished Scraping Games")

        if command.isdigit:
            print(f"Scraping {command} season")
            await scrape_season(command)

if __name__ == "__main__":
    asyncio.run(main())


