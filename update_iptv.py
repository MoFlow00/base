import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # تشغيل المتصفح مع إعدادات إخفاء الهوية
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        # تصحيح الخطأ: تغيير languages إلى locale
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale="en-US", # تم التصحيح هنا
            color_scheme='dark'
        )
        
        page = await context.new_page()

        # حقن سكريبتات لإخفاء آثار Playwright تماماً
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Connecting to {url}...")
            # استخدام commit لتجنب تعليق الشبكة في GitHub Actions
            await page.goto(url, wait_until="commit", timeout=90000)
            await asyncio.sleep(random.uniform(5, 8))

            print("Simulating activity...")
            await page.mouse.move(random.randint(100, 600), random.randint(100, 600))
            await page.evaluate("window.scrollTo(0, 300)")
            await asyncio.sleep(2)

            print("Waiting for Turnstile to unlock the button...")
            
            # فحص حالة الزر برمجياً
            try:
                await page.wait_for_function(
                    "() => { const btn = document.querySelector('#create-btn'); return btn && !btn.hasAttribute('disabled'); }",
                    timeout=150000 
                )
            except:
                print("Button remains locked. Cloudflare might be blocking the IP.")
                await page.screenshot(path="cloudflare_status.png", full_page=True)
                raise Exception("Turnstile verification failed or timed out.")

            print("Button Unlocked! Clicking...")
            await page.click("#create-btn")

            # انتظار صفحة النتائج
            await page.wait_for_selector("input[readonly]", timeout=60000)
            
            inputs = await page.locator("input[readonly]").all()
            if len(inputs) >= 3:
                username = await inputs[1].get_attribute("value")
                password = await inputs[2].get_attribute("value")
                
                print(f"✅ Success! Captured: {username}")
                
                # قراءة base.m3u وتحديثه
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()

                final = content.replace("{USERNAME}", username).replace("{PASSWORD}", password)
                
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(final)
                print("final.m3u generated successfully.")
            else:
                print("❌ Result fields not found.")

        except Exception as e:
            print(f"❌ Error Detail: {e}")
            # أخذ لقطة شاشة للتشخيص
            if not page.is_closed():
                await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
