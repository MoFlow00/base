import asyncio
import os
import sys
from pathlib import Path

# Don't disable GPU in GitHub Actions - it can cause issues
# Remove: os.environ["ELECTRON_DISABLE_GPU"] = "1"

async def run_update():
    print("Starting CloakBrowser in GitHub Actions...")

    launch_kwargs = {
        "headless": False,  # Keep False for Cloudflare
        "humanize": True,
        # Critical for GitHub Actions
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--disable-gpu",  # This is safer than ELECTRON_DISABLE_GPU
            "--window-size=1920,1080",
            # Cloudflare specific
            "--disable-blink-features=AutomationControlled",
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
    }

    try:
        from cloakbrowser import launch_context_async
    except ImportError:
        print("cloakbrowser not installed")
        sys.exit(1)

    context = None
    page = None

    try:
        print("Launching browser with Cloudflare bypass...")
        context = await launch_context_async(**launch_kwargs)
        page = await context.new_page()

        # Add stealth scripts for Cloudflare
        await page.add_init_script("""
            // Overwrite navigator properties to avoid detection
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false
            });
            
            // Overwrite chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Overwrite permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({state: Notification.permission}) :
                originalQuery(parameters)
            );
            
            // Overwrite plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Overwrite languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        url = "https://freeiptv2023-d.ottc.xyz/?action=view"
        print(f"Opening URL: {url}")

        # Add proper headers
        await page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        })

        # Navigate with longer timeout and wait for network idle
        await page.goto(
            url,
            wait_until="networkidle",
            timeout=120000
        )

        print("Page loaded. Simulating human behavior...")
        
        # Wait a bit for Cloudflare challenge
        await asyncio.sleep(5)
        
        # Check if Cloudflare challenge is present
        try:
            cf_challenge = await page.locator('#challenge-form, .cf-browser-verification, #cf-challenge').first.wait_for(state='visible', timeout=10000)
            print("Cloudflare challenge detected, waiting...")
            await asyncio.sleep(10)
        except:
            print("No Cloudflare challenge detected")
        
        # More human-like behavior
        await page.bring_to_front()
        await asyncio.sleep(2)
        
        # Random mouse movements
        await page.mouse.move(300, 300)
        await asyncio.sleep(1)
        await page.mouse.move(500, 400)
        await asyncio.sleep(1)
        await page.mouse.wheel(0, 300)
        await asyncio.sleep(1)
        await page.mouse.move(400, 350)
        await asyncio.sleep(3)

        print("Looking for create button...")
        # Try multiple selectors in case the ID is different
        selectors = [
            "#create-btn",
            "button:has-text('Create')",
            "a:has-text('Create')",
            "[onclick*='create']",
            "button:has-text('New')",
            "button:has-text('Generate')"
        ]
        
        clicked = False
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                await page.click(selector, force=True)
                print(f"Clicked using selector: {selector}")
                clicked = True
                break
            except:
                continue
        
        if not clicked:
            print("Warning: Could not find create button, checking page content...")
            content = await page.content()
            print(f"Page title: {await page.title()}")
            # Save debug screenshot
            await page.screenshot(path="debug_page.png")

        print("Waiting for credentials fields...")
        
        # Wait longer for credentials to appear
        await asyncio.sleep(5)
        
        try:
            await page.wait_for_selector(
                "input[readonly]",
                timeout=60000
            )
        except:
            print("No readonly inputs found, trying other selectors...")
            # Try other selectors
            try:
                await page.wait_for_selector(
                    "input:not([type='submit']):not([type='button'])",
                    timeout=30000
                )
            except:
                print("Could not find any input fields")
                await page.screenshot(path="error_debug.png")
                return

        # Get all input fields that might contain credentials
        inputs = await page.locator("input").all()
        print(f"Total inputs found: {len(inputs)}")
        
        # Try to find username and password fields
        user = None
        pw = None
        
        for i, inp in enumerate(inputs):
            try:
                val = await inp.get_attribute("value")
                id_attr = await inp.get_attribute("id")
                name_attr = await inp.get_attribute("name")
                placeholder = await inp.get_attribute("placeholder")
                
                print(f"Input {i}: id={id_attr}, name={name_attr}, placeholder={placeholder}, value={val}")
                
                if val and len(val) > 3:
                    if not user:
                        user = val
                    elif not pw:
                        pw = val
            except:
                continue

        if user and pw:
            print(f"USERNAME: {user}")
            print(f"PASSWORD: {pw}")

            # Use GitHub Actions workspace path
            workspace = os.environ.get('GITHUB_WORKSPACE', '.')
            base_file = os.path.join(workspace, "base.m3u")
            final_file = os.path.join(workspace, "final.m3u")

            if os.path.exists(base_file):
                with open(base_file, "r", encoding="utf-8") as f:
                    content = f.read()

                content = content.replace("{USERNAME}", user)
                content = content.replace("{PASSWORD}", pw)

                with open(final_file, "w", encoding="utf-8") as f:
                    f.write(content)

                print("✅ final.m3u generated successfully")
            else:
                print(f"⚠️ base.m3u not found at {base_file}")
                # Create a simple base.m3u if missing
                default_content = "#EXTM3U\n#EXTINF:-1,IPTV Channel\nhttp://{USERNAME}:{PASSWORD}@example.com/stream\n"
                with open(base_file, "w", encoding="utf-8") as f:
                    f.write(default_content)
                
                with open(base_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                content = content.replace("{USERNAME}", user)
                content = content.replace("{PASSWORD}", pw)
                
                with open(final_file, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("✅ Created base.m3u and final.m3u")
        else:
            print("❌ Could not extract both username and password")
            if user:
                print(f"Only found username: {user}")
            if pw:
                print(f"Only found password: {pw}")

        # Save debug screenshot
        screenshot_path = os.path.join(os.environ.get('GITHUB_WORKSPACE', '.'), "debug_screenshot.png")
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")

        await asyncio.sleep(5)

    except Exception as e:
        print(f"❌ Execution error: {e}")
        if page:
            try:
                error_path = os.path.join(os.environ.get('GITHUB_WORKSPACE', '.'), "error_debug.png")
                await page.screenshot(path=error_path)
                print(f"Error screenshot saved: {error_path}")
            except:
                pass
        raise e

    finally:
        if context:
            await context.close()
        print("Browser closed")

if __name__ == "__main__":
    asyncio.run(run_update())
