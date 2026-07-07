import asyncio
from cloakbrowser import launch_context_async

async def test():
    print("start")

    browser = await launch_context_async(
        headless=True
    )

    page = await browser.new_page()

    await page.goto("https://google.com")

    print(await page.title())

    await browser.close()

asyncio.run(test())
