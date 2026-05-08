import asyncio
import os
import random
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # التغيير الجوهري: استخدام Firefox بدلاً من Chromium
        browser = await p.firefox.launch(headless=True)
        
        # إعدادات متقدمة للهوية
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            viewport={'width': 1920, 'height': 1080},
            locale="en-US",
            timezone_id="Europe/London"
        )
        
        page = await context.new_page()

        # حقن سكريبت التخفي اليدوي
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Connecting to {url} via Firefox...")
            # الانتظار حتى 'commit' لتقليل احتمالية الـ Timeout
            await page.goto(url, wait_until="commit", timeout=90000)
            
            # محاكاة بشرية: انتظار عشوائي وحركة بسيطة
            await asyncio.sleep(random.uniform(5, 10))
            await page.mouse.move(random.randint(100, 500), random.randint(100, 500))

            print("Waiting for Turnstile to unlock...")
            
            # مراقبة الزر برمجياً بمهلة 3 دقائق
            create_btn = page.locator("#create-btn")
            await page.wait_for_function(
                "() => { const btn = document.querySelector('#create-btn'); return btn && !btn.hasAttribute('disabled'); }",
                timeout=180000
            )

            print("Button Unlocked! Clicking...")
            # نقرة بشرية مع تأخير بسيط
            await create_btn.click(delay=random.randint(100, 500))

            # انتظار صفحة النتائج
            await page.wait_for_selector("input[readonly]", timeout=60000)
            
            inputs = await page.locator("input[readonly]").all()
            if len(inputs) >= 3:
                username = await inputs[1].get_attribute("value")
                password = await inputs[2].get_attribute("value")
                
                print(f"✅ Extracted: {username}")
                
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()

                final = content.replace("{USERNAME}", username).replace("{PASSWORD}", password)
                
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(final)
                print("final.m3u updated.")
            else:
                raise Exception("Data fields not found after click.")

        except Exception as e:
            print(f"❌ Error Detail: {e}")
            if not page.is_closed():
                await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
