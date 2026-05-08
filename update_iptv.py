import asyncio
import random
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # هنرجع لـ Chromium بس بإعدادات "صايعة" المرة دي
        browser = await p.chromium.launch(headless=True)
        
        # إعدادات Context بتوحي إننا "مستخدم حقيقي" جاي من بحث جوجل
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            extra_http_headers={
                "Referer": "https://www.google.com/",
                "Accept-Language": "en-US,en;q=0.9"
            }
        )
        
        page = await context.new_page()

        # إخفاء هوية البوت تماماً
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
        """)

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print("Targeting site with Google Referer...")
            # المرة دي هندخل ببطء ونعمل محاكاة انتظار
            await page.goto(url, wait_until="commit", timeout=90000)
            
            # حركة عشوائية للماوس فوق مكان الـ Turnstile لإجباره على التحميل
            print("Simulating human movement over the widget area...")
            await page.mouse.move(300, 400)
            await asyncio.sleep(5)
            await page.mouse.wheel(0, 100)

            # محاولة "التكتكة" داخل الـ Iframe لو موجود
            # Cloudflare Turnstile غالباً بيتحط جوه iframe
            frames = page.frames
            for frame in frames:
                if "cloudflare" in frame.url:
                    print("Cloudflare frame detected! Trying to interact...")
                    await page.mouse.click(300, 450) # ضغطة في منطقة الـ widget

            print("Waiting for Turnstile callback...")
            
            # مراقبة الزرار: هل الـ disabled هتشال؟
            # زودنا الوقت لـ 4 دقائق لأن السيرفرات تقيلة
            await page.wait_for_function(
                "() => { const b = document.querySelector('#create-btn'); return b && !b.disabled; }",
                timeout=240000
            )

            print("Success! Button unlocked.")
            await page.click("#create-btn")

            # استخراج البيانات
            await page.wait_for_selector("input[readonly]", timeout=60000)
            inputs = await page.locator("input[readonly]").all()
            
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            
            if user and pw:
                print(f"Captured: {user}")
                with open("base.m3u", "r", encoding="utf-8") as f:
                    data = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(data)
                print("final.m3u is ready.")
            
        except Exception as e:
            print(f"Critical Failure: {e}")
            await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
