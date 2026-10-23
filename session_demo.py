import asyncio
import time

from sniffer.replay import get_with_retry, make_client
from sniffer.session import login_and_get_cookies

HOME = "https://quotes.toscrape.com/"


def looks_logged_in(html: str) -> bool:
    return "Logout" in html


async def main() -> None:
    async with make_client() as anon:
        r = await get_with_retry(anon, HOME)
        print(f"without cookies -> logged in: {looks_logged_in(r.text)}")

    print("Logging in with Playwright ...")
    cookies = await login_and_get_cookies("admin", "admin")
    print(f"cookies received: {list(cookies)}")

    async with make_client(cookies) as authed:
        t0 = time.perf_counter()
        r = await get_with_retry(authed, HOME)
        first = time.perf_counter() - t0
        print(f"with cookies    -> logged in: {looks_logged_in(r.text)} ({first:.2f}s)")

        t1 = time.perf_counter()
        await get_with_retry(authed, HOME)
        second = time.perf_counter() - t1
        print(f"second call, same connection: {second:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())