from playwright.async_api import async_playwright

LOGIN_URL = "https://quotes.toscrape.com/login"


async def login_and_get_cookies(username: str, password: str) -> dict[str, str]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(LOGIN_URL, wait_until="domcontentloaded")
        await page.locator("#username").fill(username)
        await page.locator("#password").fill(password)
        await page.locator("input[type='submit']").click()
        await page.get_by_role("link", name="Logout").wait_for()
        cookies = await context.cookies()
        await browser.close()
    return {c["name"]: c["value"] for c in cookies}