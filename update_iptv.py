import asyncio
import os
from cloakbrowser import launch_context_async

async def scrape_logic():
    print("🚀 Launching CloakBrowser on GitHub Runner...")
    
    # Using source-level patches to bypass Cloudflare Turnstile
    context = await launch_context_async(
        headless=True,
        humanize=True, # Human-like behavior
        args=["--no-sandbox"]
    )

    page = await context.new_page()
    url = "https://freeiptv2023-d.ottc.xyz/?action=view"

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        print("⏳ Bypassing Turnstile...")

        # Wait for the button to become active (C++ patches handle the heavy lifting)
        await page.wait_for_function(
            "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
            timeout=90000
        )

        print("✅ Button Unlocked. Extracting...")
        await page.click("#create-btn")

        # Wait for the readonly data fields
        await page.wait_for_selector("input[readonly]", timeout=30000)
        inputs = await page.locator("input[readonly]").all()
        
        if len(inputs) >= 3:
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            print(f"🎯 Captured: {user}")

            # Update the local file
            if os.path.exists("base.m3u"):
                with open("base.m3u", "r") as f:
                    content = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                with open("final.m3u", "w") as f:
                    f.write(content)
                print("📝 final.m3u updated.")

    except Exception as e:
        print(f"❌ Execution Failed: {e}")
    finally:
        await context.close()

if __name__ == "__main__":
    asyncio.run(scrape_logic())
