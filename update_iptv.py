import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # بروكسي مجاني للتجربة (تغيير الـ IP هو مفتاح الحل لـ Cloudflare)
        # ملاحظة: البروكسيات المجانية قد تكون بطيئة، لو فشلت هنغيرها
        proxy_list = [
            "http://43.152.113.120:80",
            "http://154.21.155.149:80"
        ]
        
        selected_proxy = random.choice(proxy_list)
        print(f"Attempting with Proxy: {selected_proxy}")

        try:
            browser = await p.chromium.launch(
                headless=True,
                proxy={"server": selected_proxy},
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
            )
        except:
            print("Proxy failed to launch, trying direct connection...")
            browser = await p.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            extra_http_headers={"Referer": "https://www.google.com/"}
        )
        
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Navigating to {url}...")
            # استخدام commit وانتظار يدوي لضمان التحميل خلف الـ Proxy
            await page.goto(url, wait_until="commit", timeout=90000)
            await asyncio.sleep(10) # مهلة زيادة للـ Turnstile يحمل

            print("Waiting for button to unlock...")
            create_btn = page.locator("#create-btn")
            
            # مراقبة الزر بمهلة 4 دقائق (البروكسي المجاني بطيء)
            await page.wait_for_function(
                "() => { const b = document.querySelector('#create-btn'); return b && !b.disabled; }",
                timeout=240000
            )

            print("Unblocked! Extraction in progress...")
            await create_btn.click()

            await page.wait_for_selector("input[readonly]", timeout=60000)
            inputs = await page.locator("input[readonly]").all()
            
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            
            if user and pw:
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"✅ Success: {user}")
            
        except Exception as e:
            print(f"Operation failed: {e}")
            await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
