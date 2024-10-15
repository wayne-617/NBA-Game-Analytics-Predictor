import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import time
import asyncio

SEASONS = list(range(2016,2024))
DATA_DIR = "data"
STANDINGS_DIR = os.path.join(DATA_DIR, "standings")
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
    html = asyncio.run(fetch_data(url))

    soup = BeautifulSoup(html)
    links = soup.find_all("a") # get anchor tags
    href = [l["href"] for l in links] # parse links
    standings_pages = [f"https://basketball-reference.com{l}" for l in href] # transform links into full urls

    for url in standings_pages:
        path = os.path.join(STANDINGS_DIR, url.split("/")[-1]) # create path to file based off url
        if os.path.exists(path):
            continue # continue if page is already scraped

        html = await get_html(url, "#all_schedule") # grab html for standings table
        with open(path, "w+") as f:
            f.write(html)



async def fetch_data(url):
    html = await get_html(url, "#content .filter")
    print(html)
    return html

async def fetch_box_scores(season):
    await scrape_season(season)

for season in SEASONS:
    fetch_box_scores(season)


