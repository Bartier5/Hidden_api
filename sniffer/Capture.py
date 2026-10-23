import json
from pathlib import Path

from playwright.async_api import async_playwright, Response

OUTPUT_DIR = Path("output")
JSON_TYPES = ("application/json", "text/json")


async def capture(url: str, wait_ms: int = 3000) -> list[dict]:
    captured: list[dict] = []

    async def on_response(response: Response) -> None:
        request = response.request
        if request.resource_type not in ("xhr", "fetch"):
            return
        content_type = response.headers.get("content-type", "")
        try:
            size = len(await response.body())
        except Exception:
            size = -1
        captured.append(
            {
                "method": request.method,
                "url": response.url,
                "status": response.status,
                "content_type": content_type,
                "is_json": any(t in content_type for t in JSON_TYPES),
                "size": size,
            }
        )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        page.on("response", on_response)
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(wait_ms)
        await page.mouse.wheel(0, 4000)
        await page.wait_for_timeout(wait_ms)
        await browser.close()

    return captured


def save_log(calls: list[dict], name: str = "capture_log.json") -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(calls, indent=2), encoding="utf-8")
    return path