import asyncio
import os
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # تشغيل المتصفح مع إعدادات متقدمة
        browser = await p.chromium.launch(headless=True)
        # استخدام إعدادات متصفح كاملة
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            has_touch=True
        )
        
        page = await context.new_page()

        # تجاوز كشف البوت (Stealth)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
        """)

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Navigating to {url}...")
            # الانتظار حتى استقرار الشبكة تماماً
            await page.goto(url, wait_until="networkidle", timeout=60000)

            # حركة عشوائية للماوس لمحاكاة نشاط بشري
            await page.mouse.move(100, 100)
            await asyncio.sleep(2)
            await page.mouse.move(400, 400)

            print("Waiting for Cloudflare Turnstile to unlock...")
            
            # محاولة الانتظار لظهار الزرار
            create_btn = page.locator("#create-btn")
            
            # زيادة المهلة لـ 3 دقائق احتياطياً
            await page.wait_for_function(
                "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
                timeout=180000 
            )

            print("Button unlocked! Clicking...")
            await create_btn.click()

            # انتظار ظهور النتائج
            await page.wait_for_selector("input[readonly]", timeout=45000)
            
            inputs = await page.locator("input[readonly]").all()
            username = await inputs[1].get_attribute("value")
            password = await inputs[2].get_attribute("value")

            if username and password:
                print(f"Extracted: {username}")
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()

                updated = content.replace("{USERNAME}", username).replace("{PASSWORD}", password)

                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(updated)
                print("final.m3u generated.")
            
        except Exception as e:
            print(f"Fatal Error: {e}")
            # تصوير الشاشة عشان نعرف Cloudflare واقف عند إيه
            await page.screenshot(path="cloudflare_status.png")
            print("Screenshot saved: cloudflare_status.png")
            # إنهاء العملية بـ Error code عشان الأكشن ميكملش
            exit(1) 
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
