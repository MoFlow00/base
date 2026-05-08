# FILE: update_iptv.py

import asyncio
import os
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # تشغيل المتصفح بوضع Headless للعمل على سيرفرات GitHub
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # تجاوز كشف البوت يدوياً (Manual Stealth) لتجنب حظر GitHub IPs
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # انتظار تفعيل الزر (Turnstile Check)
            print("Waiting for credentials to generate...")
            await page.wait_for_function(
                "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
                timeout=120000
            )

            await page.click("#create-btn")
            await page.wait_for_selector("input[readonly]", timeout=30000)
            
            inputs = await page.locator("input[readonly]").all()
            
            # استخراج اليوزر والباسورد من الصفحة
            username = await inputs[1].get_attribute("value")
            password = await inputs[2].get_attribute("value")

            if username and password:
                print(f"Success! Username: {username}, Password: {password}")

                # قراءة الملف الأساسي base.m3u
                if not os.path.exists("base.m3u"):
                    print("Error: base.m3u not found!")
                    return

                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()

                # استبدال الـ placeholders
                updated_content = content.replace("{USERNAME}", username).replace("{PASSWORD}", password)

                # كتابة الملف النهائي final.m3u
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(updated_content)
                
                print("final.m3u updated.")
            else:
                print("Failed to capture credentials.")

        except Exception as e:
            print(f"Error: {e}")
            # أخذ لقطة شاشة للـ Debugging في حالة الفشل على GitHub Actions
            await page.screenshot(path="debug_github.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
