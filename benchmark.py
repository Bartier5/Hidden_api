import asyncio
import sys
import time

from playwright.async_api import async_playwright

from sniffer.export import fetch_all, fetch_all_concurrent
from sniffer.replay import fetch_page, make_client

BASE = "https://quotes.toscrape.com"


async def warm_up() -> None:
    async with make_client() as client:
        await fetch_page(client, 1)


async def api_sequential(max_pages: int) -> list[dict]:
    async with make_client() as client:
        return await fetch_all(client, max_pages=max_pages, delay=0)


async def api_concurrent(max_pages: int) -> list[dict]:
    async with make_client() as client:
        return await fetch_all_concurrent(client, concurrency=5, max_pages=max_pages)


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


async def timed(coro) -> tuple[list[dict], float]:
    start = time.perf_counter()
    rows = await coro
    return rows, time.perf_counter() - start


def authors(rows: list[dict]) -> list[str]:
    return [r["author"] for r in rows]


async def main() -> None:
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    print(f"Benchmark: {pages} pages\n")

    print("Warming up ...")
    await warm_up()

    print("\nAPI sequential:")
    seq_rows, seq_time = await timed(api_sequential(pages))

    print("\nAPI concurrent:")
    con_rows, con_time = await timed(api_concurrent(pages))

    print("\nBrowser scrape ...")
    br_rows, br_time = await timed(browser_scrape(pages))

    print("\n--- Results ---")
    print(f"API sequential: {len(seq_rows)} quotes in {seq_time:.2f}s")
    print(f"API concurrent: {len(con_rows)} quotes in {con_time:.2f}s")
    print(f"Browser:        {len(br_rows)} quotes in {br_time:.2f}s")
    print(f"Concurrent vs browser:    {br_time / con_time:.1f}x")
    print(f"Concurrent vs sequential: {seq_time / con_time:.1f}x")
    same = authors(seq_rows) == authors(con_rows) == authors(br_rows)
    print(f"All three identical (authors, same order): {same}")


if __name__ == "__main__":
    asyncio.run(main())