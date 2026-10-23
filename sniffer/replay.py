import asyncio

import httpx

API_URL = "https://quotes.toscrape.com/api/quotes"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
TIMEOUT = httpx.Timeout(connect=30.0, read=30.0, write=10.0, pool=10.0)
RETRY_STATUS = {429, 500, 502, 503, 504}


def make_client(cookies: dict | None = None) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers=HEADERS,
        timeout=TIMEOUT,
        cookies=cookies,
        follow_redirects=True,
    )


async def get_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: dict | None = None,
    retries: int = 3,
) -> httpx.Response:
    for attempt in range(1, retries + 1):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            retryable = (
                isinstance(exc, httpx.TransportError)
                or exc.response.status_code in RETRY_STATUS
            )
            if not retryable or attempt == retries:
                raise
            wait = 2**attempt
            print(f"  attempt {attempt} failed ({type(exc).__name__}), retrying in {wait}s")
            await asyncio.sleep(wait)


async def fetch_page(client: httpx.AsyncClient, page_number: int) -> dict:
    response = await get_with_retry(client, API_URL, params={"page": page_number})
    return response.json()