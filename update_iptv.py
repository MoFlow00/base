import asyncio
import os
import subprocess
import sys
import requests
import random
from datetime import datetime

# --- Configuration (جلب البيانات آلياً من الـ Secrets) ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8843435187:AAGIrQnBPbsyXu959Oq95MGIvo92Q9JTeGM")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "365163909")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
base_file = os.path.join(BASE_DIR, "base.m3u")
final_file = os.path.join(BASE_DIR, "final.m3u")

# --- Telegram Notification Functions ---
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("[Telegram] Message sent.")
    except Exception as e:
        print(f"[Telegram Error] {e}")

async def send_photo(path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "HTML"}
    try:
        with open(path, "rb") as photo_file:
            files = {"photo": photo_file}
            response = requests.post(url, data=payload, files=files, timeout=30)
            response.raise_for_status()
            print(f"[Telegram] Photo sent: {path}")
    except Exception as e:
        print(f"[Telegram Error] Failed to send photo: {e}")

async def take_screenshot(page, attempt_num, suffix="debug"):
    if not page: return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_dir = os.path.join(BASE_DIR, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, f"attempt{attempt_num}_{timestamp}_{suffix}.png")
    try:
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"[Screenshot] Saved: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"[Screenshot Error] {e}")
        return None

os.environ["ELECTRON_DISABLE_GPU"] = "1"

async def run_update():
    print(f"[System] Starting Job in GitHub Actions env...")
    send_message("🚀 IPTV GitHub Action Job Started")

    launch_kwargs = {
        "headless": True,  # يتم تغذيتها عبر xvfb-run رسومياً لتظهر كـ False للموقع
        "humanize": True,  # ميزة التخفي البشري المدمجة في CloakBrowser
    }

    try:
        from cloakbrowser import launch_context_async
    except ImportError:
        print("[Error] cloakbrowser missing")
        send_message("❌ Script Error: cloakbrowser not installed.")
        sys.exit(1)

    final_context = None
    attempts_used = 0
    script_success = False

    try:
        for attempt_num in range(1, 4):
            attempts_used = attempt_num
            context = None
            page = None
            print(f"\n--- Starting Attempt {attempt_num} ---")

            try:
                context = await launch_context_async(**launch_kwargs)
                final_context = context
                page = await context.new_page()

                # إعدادات إضافية قياسية لتحديث الـ User-Agent وإخفاء الـ Webdriver بدون مكتبات خارجية
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
                })
                await page.evaluate("() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}) }")

                url = "https://freeiptv2023-d.ottc.xyz/?action=view"
                print(f"[Browser] Navigating to: {url}")
                await page.goto(url, wait_until="networkidle", timeout=90000)

                # انتظار عشوائي محاكي للبشر
                await asyncio.sleep(random.uniform(12, 16))

                # فحص محتوى الصفحة وإعادة المحاولة عند الحاجة
                for reload_check in range(1, 4):
                    content = await page.content()
                    needs_reload = False

                    if "are you a robot?" in content.lower() or "request has been denied" in content.lower():
                        needs_reload = True

                    create_btn_locator = page.locator("#create-btn")
                    is_create_btn_visible = False
                    try:
                        is_create_btn_visible = await create_btn_locator.is_visible(timeout=5000)
                    except:
                        is_create_btn_visible = False

                    if not is_create_btn_visible:
                        needs_reload = True

                    if needs_reload and reload_check < 3:
                        print(f"[Browser] Anti-bot screen detected, reloading ({reload_check}/3)...")
                        await page.reload(wait_until="networkidle", timeout=90000)
                        await asyncio.sleep(15)
                    else:
                        break

                print("[Browser] Clicking #create-btn...")
                await page.click("#create-btn", force=True)

                print("[Browser] Waiting for read-only credentials inputs...")
                await page.wait_for_selector("input[readonly]", timeout=90000)

                inputs = await page.locator("input[readonly]").all()
                print(f"[Browser] Inputs found: {len(inputs)}")

                if len(inputs) >= 3:
                    user = await inputs[1].get_attribute("value")
                    pw = await inputs[2].get_attribute("value")

                    print(f"[Data] USERNAME: {user} | PASSWORD: {pw}")

                    if os.path.exists(base_file):
                        with open(base_file, "r", encoding="utf-8") as f:
                            m3u_content = f.read()

                        m3u_content = m3u_content.replace("{USERNAME}", user).replace("{PASSWORD}", pw)

                        with open(final_file, "w", encoding="utf-8") as f:
                            f.write(m3u_content)

                        print(f"[File] final.m3u updated locally at: {final_file}")
                        script_success = True
                        break
                    else:
                        raise Exception(f"base.m3u missing at {base_file}")
                else:
                    raise Exception(f"Inputs mismatch, found {len(inputs)}")

            except Exception as e:
                error_message = str(e)
                print(f"[Error] Attempt {attempt_num} failed: {error_message}")
                screenshot_path = await take_screenshot(page, attempt_num, "error")
                
                caption_text = f"⚠️ <b>Attempt {attempt_num} Failed</b>\n<pre>{error_message[:200]}</pre>"
                if attempt_num == 3:
                    caption_text = f"🚨 <b>Final Action Failure</b>\n<pre>{error_message[:200]}</pre>"

                if screenshot_path:
                    await send_photo(screenshot_path, caption=caption_text)
                else:
                    send_message(caption_text)

                if context: await context.close()
                if attempt_num == 3: raise e

    finally:
        if final_context: await final_context.close()
        if script_success:
            send_message(f"✅ <b>IPTV Updated Successfully on GitHub Server</b>\nAttempts Used: {attempts_used}")

if __name__ == "__main__":
    asyncio.run(run_update())
