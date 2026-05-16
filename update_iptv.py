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
        
        print("⏳ Waiting for Turnstile...")
        await page.wait_for_function(
            "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
            timeout=90000
        )

        print("✅ Protection Bypassed! Sleeping 3s for human behavior...")
        await asyncio.sleep(3)

        print("🖱️ Clicking Create Button...")
        await page.click("#create-btn")
        
        print("⏳ Waiting for navigation and network to settle...")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5) # وقت إضافي لضمان نزول البيانات

        # التحقق من الحقول
        inputs = await page.locator("input[readonly]").all()
        
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
            print("❌ Fields found but not matching expected count. Dumping page source below:")
            body_text = await page.inner_text("body")
            print(f"\n--- PAGE BODY CONTENT ---\n{body_text}\n-------------------------")
            raise RuntimeError("Credentials inputs not found on the current page context.")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        # طباعة الرابط الحالي وقت الخطأ للتشخيص
        print(f"📍 Current URL when failed: {page.url}")
        try:
            body_text = await page.inner_text("body")
            print(f"\n--- FALLBACK PAGE BODY CONTENT ---\n{body_text}\n-------------------------")
        except:
            pass
        raise e
    finally:
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_update())
