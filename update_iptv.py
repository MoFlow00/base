import asyncio
import os
from cloakbrowser import launch_context_async

async def run_update():
    print("🚀 Starting CloakBrowser Stealth Engine via WireGuard Tunnel...")
    
    launch_kwargs = {
        "headless": True,
        "humanize": True,
        "args": ["--no-sandbox", "--disable-dev-shm-usage"]
    }

    context = await launch_context_async(**launch_kwargs)
    page = await context.new_page()
    url = "https://freeiptv2023-d.ottc.xyz/?action=view"

    try:
        print(f"🔗 Navigating directly to {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("⏳ Passing Turnstile Protection...")
        await page.wait_for_function(
            "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
            timeout=90000
        )

        await asyncio.sleep(3)
        print("🖱️ Clicking Create Button...")
        await page.click("#create-btn")
        
        print("⏳ Waiting for credentials fields...")
        await page.wait_for_selector("input[readonly]", timeout=30000)
        inputs = await page.locator("input[readonly]").all()
        
        if len(inputs) >= 3:
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            print(f"🎯 SUCCESS! Extracted User: {user}")

            if os.path.exists("base.m3u"):
                with open("base.m3u", "r") as f:
                    content = f.read()
                content = content.replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                with open("final.m3u", "w") as f:
                    f.write(content)
                print("📝 final.m3u updated successfully.")
            else:
                print("⚠️ base.m3u not found in repository root.")
        else:
            print("❌ Input fields found but structure mismatched.")
            body_text = await page.inner_text("body")
            print(f"Page Content Summary:\n{body_text[:500]}")
            raise RuntimeError("Credentials inputs structured differently.")
                
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        try:
            body_text = await page.inner_text("body")
            print(f"Fallback Page Content:\n{body_text[:500]}")
        except:
            pass
        raise e
    finally:
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_update())
