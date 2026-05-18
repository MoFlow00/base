import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_update_selenium():
    print("🚀 Starting Selenium Stealth Engine (Windows Persistent Context)...")
    
    options = Options()
    
    # ربط الكاش لضمان تخطي حماية كلوفلير في المرات القادمة بسلاسة
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # كتم أخطاء الشبكة والـ DNS الناتجة عن الـ Hotspot
    options.add_argument('--log-level=3')
    options.add_argument('--silent')
    options.add_argument('--disable-webrtc')
    
    # إعدادات تخطي كشف الـ Automation
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    
    # حقن كود التخفي لمنع كشف المتصفح عبر الجافا سكريبت
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    url = "https://freeiptv2023-d.ottc.xyz/?action=view"

    try:
        print(f"🔗 Navigating directly to {url}")
        driver.get(url)
        
        print("⏳ Passing Turnstile Protection...")
        print("Note: If a checkbox appears, please click it manually.")
        
        # الانتظار حتى يتفعل الزر ويختفي منه الـ 'disabled' (حد أقصى دقيقتين)
        wait = WebDriverWait(driver, 120)
        create_btn = wait.until(EC.element_to_be_clickable((By.ID, "create-btn")))

        time.sleep(3) # محاكاة التأخير البشري قبل الضغط كما في كودك الأصلي
        print("鼠标 Clicking Create Button...")
        create_btn.click()
        
        print("⏳ Waiting for credentials fields...")
        # الانتظار حتى تظهر الحقول المقروءة فقط
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[readonly]")))
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[readonly]")
        
        if len(inputs) >= 3:
            user = inputs[1].get_attribute("value")
            pw = inputs[2].get_attribute("value")
            print(f"🎯 SUCCESS! Extracted User: {user}")

            # منطق معالجة ملف الـ M3U الخاص بك
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
