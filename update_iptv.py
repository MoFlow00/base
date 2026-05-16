import asyncio
import os
from cloakbrowser import launch_context_async

async def run_update():
    print("🚀 Starting CloakBrowser Stealth Engine...")
    
    context = await launch_context_async(
        headless=True,
        humanize=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )

    page = await context.new_page()
    url = "https://freeiptv2023-d.ottc.xyz/?action=view"

    try:
        print(f"🔗 Navigating to {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("⏳ Waiting for Turnstile (Stealth Mode Active)...")
        await page.wait_for_function(
            "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
            timeout=90000
        )

        print("✅ Protection Bypassed! Clicking...")
        await page.click("#create-btn")

        # استنى شوية بعد الـ Click
        print("⏳ Waiting for page to settle after click...")
        await page.wait_for_timeout(5000)
        await page.wait_for_load_state("networkidle", timeout=30000)

        # جرب تستنى العناصر
        print("🔍 Looking for input fields...")
        await page.wait_for_selector("input[readonly]", timeout=60000)
        
        inputs = await page.locator("input[readonly]").all()
        print(f"📊 Found {len(inputs)} readonly inputs")
        
        if len(inputs) >= 3:
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            print(f"🎯 SUCCESS! Extracted User: {user}")

            if os.path.exists("base.m3u"):
                with open("base.m3u", "r") as f:
                    content = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                with open("final.m3u", "w") as f:
                    f.write(content)
                print("📝 final.m3u updated.")
            else:
                print("⚠️ base.m3u not found in repository!")

        else:
            print(f"⚠️ Expected 3+ inputs, found {len(inputs)}")
            await page.screenshot(path="debug_screenshot.png", full_page=True)
            # احفظ الـ HTML عشان تشوف العناصر
            html = await page.content()
            with open("page_source.html", "w") as f:
                f.write(html)

    except Exception as e:
        await page.screenshot(path="error_screenshot.png", full_page=True)
        html = await page.content()
        with open("page_source.html", "w") as f:
            f.write(html)
        print(f"❌ Error during execution: {e}")
        print("Page HTML preview:")
        print(html[:3000])
    finally:
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_update())
