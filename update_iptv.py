import asyncio
import os
import sys
import urllib.request
from cloakbrowser import launch_context_async

async def run_update():
    print("🚀 Starting CloakBrowser Stealth Engine via GitHub Actions Scheduler...")
    
    launch_kwargs = {
        "headless": True,
        "humanize": True,
        "args": [
            "--no-sandbox", 
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--allow-elevated-browser"
        ]
    }

    context = await launch_context_async(**launch_kwargs)
    page = await context.new_page()
    url = "https://freeiptv2023-d.ottc.xyz/?action=view"

    try:
        print(f"🔗 Navigating to {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("⏳ Waiting for Turnstile (Stealth Mode Active)...")
        await page.wait_for_function(
            "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
            timeout=120000
        )

        print("✅ Protection Bypassed! Clicking...")
        await page.click("#create-btn")

        await page.wait_for_selector("input[readonly]", timeout=30000)
        inputs = await page.locator("input[readonly]").all()
        
        if len(inputs) >= 3:
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            print(f"🎯 SUCCESS! Extracted User: {user}")

            current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()
            base_file = os.path.join(current_dir, "base.m3u")
            final_file = os.path.join(current_dir, "final.m3u")

            # إذا لم يجد الملف محلياً في السيرفر، يقوم بسحبه من الرابط الذي أرفقته فوراً
            if not os.path.exists(base_file):
                print("📥 Fetching base.m3u directly from GitHub...")
                raw_url = "https://raw.githubusercontent.com/MoFlow00/base/main/base.m3u"
                urllib.request.urlretrieve(raw_url, base_file)

            with open(base_file, "r", encoding="utf-8") as f:
                content = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
            with open(final_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"📝 final.m3u updated successfully.")
            
        else:
            print("❌ Input fields structure mismatched.")
            raise RuntimeError("Structure mismatched.")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        raise e
    finally:
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_update())
