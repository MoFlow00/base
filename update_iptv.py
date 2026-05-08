import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # تشغيل كروميوم مع محاكاة قوية
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        
        # محاكاة موبايل (iPhone) لتقليل ريبة Cloudflare
        iphone = p.devices['iPhone 14 Pro Max']
        context = await browser.new_context(
            **iphone,
            locale="en-US"
        )
        
        page = await context.new_page()

        # إخفاء الهوية البرمجية
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Opening {url} with Mobile Profile...")
            await page.goto(url, wait_until="domcontentloaded", timeout=90000)
            
            # حركة عشوائية لفك تعليق Turnstile
            print("Simulating human touches...")
            await page.mouse.move(random.randint(100, 300), random.randint(100, 300))
            await asyncio.sleep(5)

            # التكتيك الجديد: البحث عن الـ Iframe والضغط بداخله
            print("Searching for Turnstile checkbox...")
            frames = page.frames
            for frame in frames:
                if "cloudflare" in frame.url:
                    # محاولة الضغط في نص الفريم (مكان الـ Checkbox غالباً)
                    box = await page.locator('iframe[src*="cloudflare"]').bounding_box()
                    if box:
                        print("Found Cloudflare frame. Clicking center...")
                        await page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
            
            print("Waiting for button to unlock...")
            # مراقبة الزر (المهلة 3 دقائق)
            await page.wait_for_function(
                "() => { const btn = document.querySelector('#create-btn'); return btn && !btn.hasAttribute('disabled'); }",
                timeout=180000
            )

            print("Success! Button Unlocked. Clicking...")
            await page.click("#create-btn")

            # انتظار النتائج
            await page.wait_for_selector("input[readonly]", timeout=45000)
            inputs = await page.locator("input[readonly]").all()
            
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            
            if user and pw:
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()
                
                final_data = content.replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(final_data)
                print(f"✅ Extracted: {user}")

        except Exception as e:
            print(f"Failed: {e}")
            await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
