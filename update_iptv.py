import asyncio
import os
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # تشغيل عادي جداً لأن النفق شغال على مستوى النظام
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print("Connecting through WireGuard tunnel...")
            await page.goto(url, wait_until="load", timeout=90000)

            print("Waiting for Turnstile unlock (WARP mode)...")
            # الانتظار حتى تفعيل الزر
            await page.wait_for_function(
                "() => { const btn = document.querySelector('#create-btn'); return btn && !btn.hasAttribute('disabled'); }",
                timeout=120000
            )

            print("Success! Clicking button...")
            await page.click("#create-btn")

            await page.wait_for_selector("input[readonly]", timeout=45000)
            inputs = await page.locator("input[readonly]").all()
            
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            
            if user and pw:
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", password)
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Extracted: {user}")

        except Exception as e:
            print(f"Failed: {e}")
            await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
