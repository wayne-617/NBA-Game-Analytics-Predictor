import os
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import time
import asyncio

SEASONS = list(range(2016,2024))
DATA_DIR = "data"
STANDINGS_DIR = os.path.join(DATA_DIR, "standings")
SCORES_DIR = os.path.join(DATA_DIR, "scores")

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
    
season = 2016
url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games.html"

async def fetch_data(url):
    html = await get_html(url, "#content .filter")
    print(html)

asyncio.run(fetch_data(url))