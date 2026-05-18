import asyncio
import os
import sys
from cloakbrowser import launch_context_async

async def run_update():
    # التحقق تلقائياً إذا كان الكود يعمل داخل سيرفرات GitHub
    is_github = "GITHUB_ACTIONS" in os.environ
    
    print("🚀 Starting CloakBrowser Stealth Engine via Playwright...")
    
    launch_kwargs = {
        "headless": True if is_github else False, # صامت في جيت هاب، مرئي على اللابتوب لضمان التخطي
        "humanize": True,
        "args": ["--no-sandbox", "--disable-dev-shm-usage"]
    }

    # تفعيل ملف تعريف الكاش محلياً فقط على اللابتوب لحفظ الكوكي
    if not is_github:
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        launch_kwargs["user_data_dir"] = user_data_dir

    context = await launch_context_async(**launch_kwargs)
    page = await context.new_page()
    url = "https://freeiptv2023-d.ottc.xyz/?action=view"

    try:
        print(f"🔗 Navigating directly to {url}")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        print("⏳ Passing Turnstile Protection...")
        # انتظار فك قفل الحماية من كلوفلير (دقيقتين كحد أقصى)
        await page.wait_for_function(
            "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
            timeout=120000
        )

        await asyncio.sleep(5) # الانتظار المقترح من الموقع لضمان جاهزية السيرفر
        print("🖱️ Clicking Create Button...")
        await page.click("#create-btn")
        
        print("⏳ Waiting for credentials fields...")
        await page.wait_for_selector("input[readonly]", timeout=30000)
        inputs = await page.locator("input[readonly]").all()
        
        if len(inputs) >= 3:
            user = await inputs[1].get_attribute("value")
            pw = inputs[2].get_attribute("value")
            print(f"🎯 SUCCESS! Extracted User: {user}")

            # تحديث ملف الـ M3U
            if os.path.exists("base.m3u"):
                with open("base.m3u", "r", encoding="utf-8") as f:
                    content = f.read()
                content = content.replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                with open("final.m3u", "w", encoding="utf-8") as f:
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
        # أخذ سكرين شوت برمجية للتحليل في حال تعثر الـ Playwright
        await page.screenshot(path="error_debug.png")
        raise e
    finally:
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_update())
