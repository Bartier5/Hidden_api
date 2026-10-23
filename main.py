import asyncio
import sys

from sniffer.capture import capture, save_log

DEFAULT_URL = "https://quotes.toscrape.com/scroll"


async def main() -> None:
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    print(f"Sniffing {url} ...")
    calls = await capture(url)

    if not calls:
        print("No XHR/fetch calls captured.")
        return

    for c in calls:
        tag = "JSON" if c["is_json"] else "    "
        print(f"[{tag}] {c['method']:<5} {c['status']}  {c['size']:>7} B  {c['url']}")

    path = save_log(calls)
    json_count = sum(c["is_json"] for c in calls)
    print(f"\n{len(calls)} calls captured, {json_count} JSON. Saved to {path}")


if __name__ == "__main__":
    asyncio.run(main())