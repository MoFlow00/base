import asyncio
import os
from playwright.async_api import async_playwright

async def run_logic():
    async with async_playwright() as p:
        # تشغيل المتصفح بإعدادات تتخطى حماية GitHub Actions
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # إخفاء أثر الأتمتة
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        
        try:
            print(f"Connecting to {url}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # الانتظار لتخطى Turnstile وتفعيل الزر
            await page.wait_for_function(
                "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
                timeout=120000
            )

            await page.click("#create-btn")
            await page.wait_for_selector("input[readonly]", timeout=30000)
            
            inputs = await page.locator("input[readonly]").all()
            username = await inputs[1].get_attribute("value")
            password = await inputs[2].get_attribute("value")

            if username and password:
                print(f"Extracted: {username} / {password}")
                
                # قراءة ملف الـ base وتحديثه
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()

                final_content = content.replace("{USERNAME}", username).replace("{PASSWORD}", password)

                with open("final.m3u", "w", encoding="utf-8") as f:
                    f.write(final_content)
                
                print("final.m3u has been updated successfully.")
            else:
                print("Failed to extract credentials.")

        except Exception as e:
            print(f"Error during scraping: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_logic())
