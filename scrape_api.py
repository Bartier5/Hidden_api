import asyncio
import time

from sniffer.export import fetch_all, write_csv
from sniffer.replay import make_client


async def main() -> None:
    start = time.perf_counter()
    async with make_client() as client:
        rows = await fetch_all(client)
    path = write_csv(rows)
    elapsed = time.perf_counter() - start
    print(f"\n{len(rows)} quotes saved to {path} in {elapsed:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())