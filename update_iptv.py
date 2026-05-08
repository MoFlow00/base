import asyncio
import os
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # رفع مستوى محاكاة المتصفح الحقيقي
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=1,
        )
        
        page = await context.new_page()

        # حقن سكريبت التخفي قبل الملاحة
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Connecting to {url}...")
            
            # التعديل رقم 1: الانتظار حتى 'commit' فقط (أول رد من السيرفر) لتجنب تعليق الشبكة
            await page.goto(url, wait_until="commit", timeout=90000)
            
            # التعديل رقم 2: انتظار تحميل الـ DOM يدوياً
            print("Page committed, waiting for DOM...")
            await page.wait_for_load_state("domcontentloaded")
            
            # التعديل رقم 3: مهلة انتظار ثابتة قصيرة لترك ملفات Cloudflare تحمل
            await asyncio.sleep(5)

            print("Checking for Turnstile / Create Button...")
            
            # التعديل رقم 4: محاولة الوصول للزرار بمهلة زمنية أطول
            create_btn = page.locator("#create-btn")
            
            # ننتظر حتى يصبح الزرار مرئياً ومفعلاً
            await page.wait_for_function(
                "() => { const btn = document.querySelector('#create-btn'); return btn && !btn.hasAttribute('disabled'); }",
                timeout=120000
            )

            print("Button is active! Clicking...")
            await create_btn.click()

            # انتظار صفحة النتائج
            await page.wait_for_selector("input[readonly]", timeout=60000)
            
            inputs = await page.locator("input[readonly]").all()
            if len(inputs) >= 3:
                username = await inputs[1].get_attribute("value")
                password = await inputs[2].get_attribute("value")
                
                print(f"Success! Captured: {username}")
                
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()

                final = content.replace("{USERNAME}", username).replace("{PASSWORD}", password)
                
                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(final)
                print("File final.m3u is ready.")
            else:
                raise Exception("Inputs not found on result page")

        except Exception as e:
            print(f"Error detail: {e}")
            # تصوير الشاشة ضروري جداً هنا لنعرف هل ظهرت رسالة "Access Denied"؟
            await page.screenshot(path="cloudflare_status.png", full_page=True)
            exit(1)
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
