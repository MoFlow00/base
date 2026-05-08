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
                "--disable-dev-shm-usage",
                "--window-size=1920,1080"
            ]
        )
        
        # إنشاء سياق متصفح مع User-Agent عشوائي وحقيقي
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            languages=["en-US", "en"],
            color_scheme='dark'
        )
        
        page = await context.new_page()

        # حقن سكريبتات لإخفاء آثار Playwright تماماً
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        """)

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Opening {url}...")
            # الانتقال للصفحة ببطء لمحاكاة البشر
            await page.goto(url, wait_until="commit", timeout=90000)
            await asyncio.sleep(random.uniform(3, 6))

            print("Simulating human activity to trigger Turnstile...")
            # التحرك في الصفحة وتحريك الماوس
            await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
            await page.evaluate("window.scrollTo(0, 200)")
            await asyncio.sleep(2)
            await page.evaluate("window.scrollTo(0, 0)")

            print("Waiting for button to unlock (max 120s)...")
            
            # محاولة تفعيل الزر برمجياً إذا علق الـ UI (ولكن Cloudflare قد يرفضه)
            # سننتظر التفعيل الطبيعي أولاً
            try:
                await page.wait_for_function(
                    "() => { const btn = document.querySelector('#create-btn'); return btn && !btn.hasAttribute('disabled'); }",
                    timeout=120000
                )
            except:
                print("Button didn't unlock naturally. Site might be blocking GitHub IP.")
                # محاولة أخيرة: أخذ لقطة شاشة للـ Debug
                await page.screenshot(path="cloudflare_status.png", full_page=True)
                raise Exception("Cloudflare blocked the Turnstile widget.")

            print("Button Unlocked! Clicking...")
            await page.click("#create-btn")

            # انتظار صفحة النتائج
            await page.wait_for_selector("input[readonly]", timeout=45000)
            
            inputs = await page.locator("input[readonly]").all()
            if len(inputs) >= 3:
                username = await inputs[1].get_attribute("value")
                password = await inputs[2].get_attribute("value")
                
                print(f"✅ Success! Captured: {username}")
                
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()

                final = content.replace("{USERNAME}", username).replace("{PASSWORD}", password)
                
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(final)
                print("File final.m3u updated.")
            else:
                print("❌ Data fields not found.")

        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
