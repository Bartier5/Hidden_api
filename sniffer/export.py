import asyncio
import csv
from pathlib import Path

import httpx

from sniffer.replay import fetch_page

OUTPUT_DIR = Path("output")
FIELDS = ["page", "author", "text", "tags", "author_slug"]


def flatten(quote: dict, page_number: int) -> dict:
    return {
        "page": page_number,
        "author": quote["author"]["name"],
        "text": quote["text"],
        "tags": "; ".join(quote["tags"]),
        "author_slug": quote["author"]["slug"],
    }


async def fetch_all(
    client: httpx.AsyncClient,
    max_pages: int = 50,
    delay: float = 0.2,
) -> list[dict]:
    rows: list[dict] = []
    page_number = 1
    while page_number <= max_pages:
        data = await fetch_page(client, page_number)
        for quote in data["quotes"]:
            rows.append(flatten(quote, page_number))
        print(f"  page {page_number}: {len(data['quotes'])} quotes")
        if not data["has_next"]:
            break
        page_number += 1
        await asyncio.sleep(delay)
    return rows


def write_csv(rows: list[dict], name: str = "quotes.csv") -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / name
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path
async def fetch_all_concurrent(
    client: httpx.AsyncClient,
    concurrency: int = 5,
    max_pages: int = 50,
) -> list[dict]:
    rows: list[dict] = []
    next_page = 1
    finished = False
    while not finished and next_page <= max_pages:
        wave = list(range(next_page, min(next_page + concurrency, max_pages + 1)))
        results = await asyncio.gather(*(fetch_page(client, n) for n in wave))
        for page_number, data in zip(wave, results):
            for quote in data["quotes"]:
                rows.append(flatten(quote, page_number))
            if not data["has_next"]:
                finished = True
        print(f"  wave {wave[0]}-{wave[-1]} done, {len(rows)} rows so far")
        next_page += concurrency
    return rows