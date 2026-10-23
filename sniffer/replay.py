import httpx

API_URL = "https://quotes.toscrape.com/api/quotes"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(headers=HEADERS, timeout=20.0)


async def fetch_page(client: httpx.AsyncClient, page_number: int) -> dict:
    response = await client.get(API_URL, params={"page": page_number})
    response.raise_for_status()
    return response.json()