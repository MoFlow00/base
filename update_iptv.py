import asyncio
import os
from cloakbrowser import launch_context_async

async def run_update():
    print("🚀 Starting CloakBrowser Stealth Engine...")
    
    # CloakBrowser is specifically built to pass Cloudflare Turnstile
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
        # Same logic that worked for you in Playwright
        await page.wait_for_function(
            "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
            timeout=90000
        )

        print("✅ Protection Bypassed! Clicking...")
        await page.click("#create-btn")

        # Wait for data fields
        await page.wait_for_selector("input[readonly]", timeout=30000)
        inputs = await page.locator("input[readonly]").all()
        
        if len(inputs) >= 3:
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            print(f"🎯 SUCCESS! Extracted User: {user}")

            # Update the local file if it exists
            if os.path.exists("base.m3u"):
                with open("base.m3u", "r") as f:
                    content = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                with open("final.m3u", "w") as f:
                    f.write(content)
                print("📝 final.m3u updated.")
            else:
                print("⚠️ base.m3u not found in repository!")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
    finally:
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_update())
