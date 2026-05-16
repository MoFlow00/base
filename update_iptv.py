import asyncio
import os
import requests
import random
from cloakbrowser import launch_context_async

def fetch_free_proxies():
    print("📥 Fetching fresh public proxy list...")
    # رابط موثوق ومحدث كل ساعة لبروكسيات HTTP عامة
    url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            proxies = response.text.strip().split("\n")
            return [p.strip() for p in proxies if p.strip()]
    except Exception as e:
        print(f"⚠️ Failed to fetch proxy list: {e}")
    return []

async def run_update():
    print("🚀 Starting CloakBrowser Stealth Engine...")
    
    proxy_list = fetch_free_proxies()
    if not proxy_list:
        print("⚠️ Running without proxy (fallback to GitHub IP)...")
        proxy_list = [None]
    else:
        # خلط القائمة عشوائياً عشان كل مرة يربط بـ IP مختلف
        random.shuffle(proxy_list)
        print(f"📊 Loaded {len(proxy_list)} proxies. Testing targets...")

    success = False
    # السكربت هيجرب أفضل 10 بروكسيات ورا بعض لحد ما واحد يظبط
    for current_proxy in proxy_list[:10]:
        proxy_url = f"http://{current_proxy}" if current_proxy else None
        
        launch_kwargs = {
            "headless": True,
            "humanize": True,
            "args": ["--no-sandbox", "--disable-dev-shm-usage"]
        }
        
        if proxy_url:
            print(f"🌐 Injecting Proxy: {proxy_url}")
            launch_kwargs["proxy"] = proxy_url
            launch_kwargs["geoip"] = True # لتطابق الموقع والوقت تلقائياً

        context = None
        try:
            context = await launch_context_async(**launch_kwargs)
            page = await context.new_page()
            url = "https://freeiptv2023-d.ottc.xyz/?action=view"
            
            print(f"🔗 Requesting page via proxy...")
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # فحص فوري: هل البروكسي ده محظور شبكياً من الموقع؟
            body_text = await page.inner_text("body")
            if "don't allow account registrations when you are connected to a VPN" in body_text:
                print("❌ Proxy flagged as VPN/DataCenter by the site. Rotating...")
                await context.close()
                continue
            
            print("⏳ Passing Turnstile (Stealth Engine Active)...")
            await page.wait_for_function(
                "() => !document.querySelector('#create-btn').hasAttribute('disabled')",
                timeout=60000
            )

            await asyncio.sleep(2)
            print("🖱️ Clicking Create Button...")
            await page.click("#create-btn")
            
            print("⏳ Fetching new credentials...")
            await page.wait_for_selector("input[readonly]", timeout=20000)
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
                    success = True
                    await context.close()
                    break
        except Exception as e:
            print(f"⚠️ Proxy failed or timed out: {e}")
            if context:
                try:
                    await context.close()
                except:
                    pass
            continue
    
    if not success:
        raise RuntimeError("All attempted free proxies failed to bypass the firewall.")

if __name__ == "__main__":
    asyncio.run(run_update())
