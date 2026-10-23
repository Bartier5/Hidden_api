import asyncio
import json
import sys

from sniffer.analyze import analyze, save_bodies
from sniffer.capture import capture, save_log

DEFAULT_URL = "https://quotes.toscrape.com/scroll"


async def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"Sniffing {url} ...")
    calls = await capture(url)
    log_path = save_log(calls)
    print(f"{len(calls)} XHR/fetch calls captured. Log: {log_path}")

    results = analyze(calls)
    if not results:
        print("No JSON responses found.")
        return

    print(f"\n{len(results)} JSON responses, best candidates first:\n")
    for rank, r in enumerate(results, start=1):
        print(f"#{rank}  {r['record_count']} records  {r['size']} B")
        print(f"    url:   {r['url']}")
        print(f"    shape: {r['shape']}")
        if r["first_record"] is not None:
            print(f"    first: {json.dumps(r['first_record'])[:150]}")
        print()

    folder = save_bodies(results)
    print(f"Full bodies saved in {folder}")


if __name__ == "__main__":
    asyncio.run(main())