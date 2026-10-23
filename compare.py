import asyncio
import json
import time
from pathlib import Path

from sniffer.replay import fetch_page, make_client

BODIES = Path("output") / "bodies"


def load_saved_page(page_number: int) -> dict | None:
    for path in sorted(BODIES.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("page") == page_number:
            return data
    return None


async def main() -> None:
    saved = load_saved_page(1)
    if saved is None:
        print("No saved page 1 found. Run main.py first.")
        return

    async with make_client() as client:
        start = time.perf_counter()
        fresh = await fetch_page(client, 1)
        elapsed = time.perf_counter() - start

    print(f"httpx fetched page 1 in {elapsed:.2f}s (no browser)")
    print(f"quotes returned: {len(fresh['quotes'])}, has_next: {fresh['has_next']}")
    print(f"identical to browser capture: {fresh['quotes'] == saved['quotes']}")

    print("\nFirst 3 records:")
    for q in fresh["quotes"][:3]:
        print(f"  - {q['author']['name']}  tags={q['tags'][:2]}")


if __name__ == "__main__":
    asyncio.run(main())