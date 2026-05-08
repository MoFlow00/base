import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # قائمة بروكسيات مجانية للتجربة (لو عندك بروكسي مدفوع حطه هنا)
        # البروكسيات المجانية "نصيب"، فممكن نحتاج نغيرهم
        proxies = [
            "http://20.206.106.178:80",
            "http://18.143.215.34:80",
        ]
        
        proxy_server = random.choice(proxies)
        print(f"Using Proxy: {proxy_server}")

        # تشغيل المتصفح مع البروكسي
        try:
            browser = await p.chromium.launch(
                headless=True,
                proxy={"server": proxy_server},
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )
        except:
            # لو البروكسي فشل، شغل عادي
            browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800},
            locale="en-US"
        )
        
        page = await context.new_page()

        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Attempting to connect to {url}...")
            # استخدام wait_until="load" لضمان تحميل الـ Widget بالكامل
            await page.goto(url, wait_until="load", timeout=90000)
            
            # محاكاة حركة عشوائية لفك تعليق Turnstile
            for i in range(3):
                await page.mouse.wheel(0, 200)
                await asyncio.sleep(2)
                await page.mouse.wheel(0, -200)

            print("Waiting for Turnstile to approve us...")
            
            # الانتظار حتى تفعيل الزر
            await page.wait_for_function(
                "() => { const btn = document.querySelector('#create-btn'); return btn && !btn.hasAttribute('disabled'); }",
                timeout=120000
            )

            print("Unblocked! Proceeding...")
            await page.click("#create-btn")

            await page.wait_for_selector("input[readonly]", timeout=60000)
            
            inputs = await page.locator("input[readonly]").all()
            username = await inputs[1].get_attribute("value")
            password = await inputs[2].get_attribute("value")

            with open("base.m3u", "r", encoding="utf-8") as f:
                content = f.read()

            final = content.replace("{USERNAME}", username).replace("{PASSWORD}", password)
            
            with open("final.m3u", "w", encoding="utf-8") as f:
                f.write(final)
            print("Done! final.m3u created.")

        except Exception as e:
            print(f"Failed again. Cloudflare is too strong for GitHub IPs. Error: {e}")
            await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
