import asyncio
import os
import subprocess
import sys 

async def run_update():
    print("🚀 Starting CloakBrowser Stealth Engine inside Debian (Termux)...")
    
    launch_kwargs = {
        "headless": True,
        "humanize": True,
        "args": [
            "--no-sandbox", 
            "--disable-setuid-sandbox", 
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run"
        ]
    } 

    try:
        from cloakbrowser import launch_context_async
    except ImportError:
        print("❌ Error: 'cloakbrowser' library not found.")
        sys.exit(1) 

    context = await launch_context_async(**launch_kwargs)
    page = await context.new_page()
    url = "https://freeiptv2023-d.ottc.xyz/?action=view" 

    try:
        print(f"🔗 Navigating to {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("⏳ Waiting for Turnstile & Site Timer to unlock the button naturally...")
        # الانتظار الذكي لغاية ما الموقع بنفسه يشيل الـ disabled بعد انتهاء العداد
        await page.wait_for_function(
            "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
            timeout=60000
        ) 

        await asyncio.sleep(2)
        print("🖱️ Clicking Create Button...")
        await page.click("#create-btn") 

        print("⏳ Waiting for credentials fields...")
        await page.wait_for_selector("input[readonly]", timeout=60000)
        inputs = await page.locator("input[readonly]").all()
        
        if len(inputs) >= 3:
            user = await inputs[1].get_attribute("value")
            pw = await inputs[2].get_attribute("value")
            print(f"🎯 SUCCESS! Extracted User: {user}") 

            base_file = "/root/base/base.m3u"
            final_file = "/root/base/final.m3u" 

            if os.path.exists(base_file):
                with open(base_file, "r", encoding="utf-8") as f:
                    content = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                with open(final_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print("📝 final.m3u generated successfully.")
                
                print("📤 Pushing updated final.m3u to GitHub...")
                os.chdir("/root/base")
                subprocess.run(["git", "config", "--local", "user.name", "Termux Debian Bot"], check=True)
                subprocess.run(["git", "config", "--local", "user.email", "debian@termux.bot"], check=True)
                subprocess.run(["git", "add", "final.m3u"], check=True)
                
                status = subprocess.run(["git", "commit", "-m", "📝 Auto-update final.m3u via Termux Debian"], capture_output=True, text=True)
                
                if "nothing to commit" in status.stdout:
                    print("ℹ️ No changes detected. Repository is already up to date.")
                else:
                    subprocess.run(["git", "push"], check=True)
                    print("✅ Successfully pushed to GitHub!")
            else:
                print(f"⚠️ base.m3u not found at: {base_file}")
        else:
            print("❌ Input fields structure mismatched.") 

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        try:
            await page.screenshot(path="/root/base/error_debug.png")
            print("📸 Screenshot saved as error_debug.png")
        except:
            pass
        raise e
    finally:
        await context.close() 

if __name__ == "__main__":
    asyncio.run(run_update())
