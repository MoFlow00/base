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
        
        # استخدم Promise عشان تتعامل مع الـ Navigation/Response
        # الموقع بيعمل POST لما تكبس الزرار
        async with page.expect_response("**/index.php**", timeout=30000) as response_info:
            await page.click("#create-btn")
        
        response = await response_info.value
        print(f"📡 Response status: {response.status}")
        
        # استنى شوية عشان الـ DOM يتحدث
        await page.wait_for_timeout(3000)
        await page.wait_for_load_state("networkidle", timeout=30000)

        # خد Screenshot عشان تشوف الحالة
        await page.screenshot(path="after_click.png", full_page=True)

        # جرب تدور على العناصر بأكتر من طريقة
        print("🔍 Looking for input fields...")
        
        # الأول: شوف لو فيه alert-danger (يعني error)
        alert_danger = await page.locator(".alert-danger").count()
        if alert_danger > 0:
            alert_text = await page.locator(".alert-danger").text_content()
            print(f"⚠️ Alert found: {alert_text}")
            
            # لو فيه error، جرب تكبس تاني بعد شوية
            print("🔄 Retrying after 5 seconds...")
            await page.wait_for_timeout(5000)
            
            # ريفريش وعيد
            await page.reload(wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_function(
                "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
                timeout=90000
            )
            await page.click("#create-btn")
            await page.wait_for_timeout(5000)

        # دور على الـ inputs
        selectors_to_try = [
            "input[readonly]",
            "input[readonly='readonly']", 
            "input.form-control[readonly]",
            "input#username",
            "input#password",
            "input[name='username']",
            "input[name='password']",
            "input[type='text'][readonly]",
        ]
        
        inputs = []
        for selector in selectors_to_try:
            try:
                count = await page.locator(selector).count()
                if count > 0:
                    print(f"✅ Found {count} elements with: {selector}")
                    inputs = await page.locator(selector).all()
                    break
            except:
                continue
        
        print(f"📊 Total inputs found: {len(inputs)}")
        
        if len(inputs) >= 2:
            # جرب تلاقي الـ username و password
            user = None
            pw = None
            
            for inp in inputs:
                val = await inp.get_attribute("value") or ""
                placeholder = await inp.get_attribute("placeholder") or ""
                id_attr = await inp.get_attribute("id") or ""
                name_attr = await inp.get_attribute("name") or ""
                
                print(f"🔍 Input: id={id_attr}, name={name_attr}, placeholder={placeholder}, value={val[:20] if val else 'empty'}")
                
                if val and len(val) > 3:
                    if not user:
                        user = val
                    elif not pw:
                        pw = val
            
            if user and pw:
                print(f"🎯 SUCCESS! User: {user[:10]}..., PW: {pw[:10]}...")

                if os.path.exists("base.m3u"):
                    with open("base.m3u", "r") as f:
                        content = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
                    with open("final.m3u", "w") as f:
                        f.write(content)
                    print("📝 final.m3u updated.")
                else:
                    print("⚠️ base.m3u not found!")
            else:
                print("⚠️ Could not extract credentials from inputs")
        else:
            print(f"⚠️ Expected 2+ inputs, found {len(inputs)}")
            # احفظ الـ HTML الكامل للـ Debug
            html = await page.content()
            with open("page_source.html", "w") as f:
                f.write(html)

    except Exception as e:
        await page.screenshot(path="error_screenshot.png", full_page=True)
        html = await page.content()
        with open("page_source.html", "w") as f:
            f.write(html)
        print(f"❌ Error: {e}")
        print("Page HTML preview (first 2000 chars):")
        print(html[:2000])
    finally:
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_update())
