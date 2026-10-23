import asyncio
import sys
import time

from playwright.async_api import async_playwright

from sniffer.export import fetch_all
from sniffer.replay import make_client

BASE = "https://quotes.toscrape.com"


async def api_scrape(max_pages: int) -> list[dict]:
    async with make_client() as client:
        return await fetch_all(client, max_pages=max_pages, delay=0)


async def browser_scrape(max_pages: int) -> list[dict]:
    rows: list[dict] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for n in range(1, max_pages + 1):
            await page.goto(f"{BASE}/page/{n}/", wait_until="domcontentloaded")
            quotes = page.locator(".quote")
            for i in range(await quotes.count()):
                q = quotes.nth(i)
                rows.append(
                    {
                        "author": await q.locator("small.author").inner_text(),
                        "text": await q.locator("span.text").inner_text(),
                    }
                )
        await browser.close()
    return rows


async def main() -> None:
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"Benchmark: {pages} pages\n")

    print("API scrape:")
    t0 = time.perf_counter()
    api_rows = await api_scrape(pages)
    api_time = time.perf_counter() - t0

    print("\nBrowser scrape ...")
    t1 = time.perf_counter()
    browser_rows = await browser_scrape(pages)
    browser_time = time.perf_counter() - t1

    same_count = len(api_rows) == len(browser_rows)
    same_authors = [r["author"] for r in api_rows] == [r["author"] for r in browser_rows]

    print("\n--- Results ---")
    print(f"API:     {len(api_rows)} quotes in {api_time:.2f}s")
    print(f"Browser: {len(browser_rows)} quotes in {browser_time:.2f}s")
    print(f"Speedup: {browser_time / api_time:.1f}x")
    print(f"Same count: {same_count} | Same authors in same order: {same_authors}")


if __name__ == "__main__":
    asyncio.run(main())