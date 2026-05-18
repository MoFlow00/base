import time
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_update_selenium():
    is_github = "GITHUB_ACTIONS" in os.environ
    is_headless = is_github or (len(sys.argv) > 1 and sys.argv[1] == 'headless')
    
    url = "https://freeiptv2023-d.ottc.xyz/?action=view"

    # 1. إذا كان يعمل على سيرفر GitHub الصامت
    if is_headless:
        print("🚀 Starting UNDETECTED Chromium Engine (GitHub Actions Bypass Mode)...")
        import undetected_chromedriver as uc
        
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--log-level=3')
        
        driver = uc.Chrome(options=options, version_main=120) # تجنب كشف النواة
        
    # 2. إذا كان يعمل محلياً على اللابتوب الخاص بك (الوضع المرئي المستقر)
    else:
        print("🚀 Starting Standard Selenium Engine (Local Windows Persistent Mode)...")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument('--disable-webrtc')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        driver = webdriver.Chrome(options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

    try:
        print(f"🔗 Navigating directly to {url}")
        driver.get(url)
        
        print("⏳ Passing Turnstile Protection...")
        if not is_headless:
            print("Note: If a checkbox appears on your laptop screen, please click it manually.")
        
        # انتظار فك قفل الزر (بحد أقصى دقيقتين)
        wait = WebDriverWait(driver, 120)
        create_btn = wait.until(EC.element_to_be_clickable((By.ID, "create-btn")))

        time.sleep(5) # الانتظار 5 ثوانٍ كاملة بناءً على طلب واجهة الموقع الرسمية
        print("鼠标 Clicking Create Button...")
        create_btn.click()
        
        print("⏳ Waiting for credentials fields...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[readonly]")))
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[readonly]")
        
        if len(inputs) >= 3:
            user = inputs[1].get_attribute("value")
            pw = inputs[2].get_attribute("value")
            print(f"🎯 SUCCESS! Extracted User: {user}")

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
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"Page Content Summary:\n{body_text[:500]}")
            raise RuntimeError("Credentials inputs structured differently.")
                
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"Fallback Page Content:\n{body_text[:500]}")
        except:
            pass
        driver.save_screenshot("error_debug.png")
        raise e
    finally:
        print("Cleaning up and closing browser...")
        driver.quit()

if __name__ == "__main__":
    run_update_selenium()
