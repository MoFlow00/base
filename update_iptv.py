import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_scraper():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36")

    # المسار اللي لاقيناه في جهازك
    service = Service(executable_path="/data/data/com.termux/files/usr/bin/chromedriver")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("🚀 Connecting via Mobile IP...")
        driver.get("https://freeiptv2023-d.ottc.xyz/?action=view")
        
        wait = WebDriverWait(driver, 120)
        btn = wait.until(EC.element_to_be_clickable((By.ID, "create-btn")))
        
        print("✅ Success! Clicking...")
        btn.click()
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[readonly]")))
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[readonly]")
        
        user = inputs[1].get_attribute("value")
        pw = inputs[2].get_attribute("value")
        print(f"✅ Extracted: {user}")

        # تحديث الملف
        if os.path.exists("base.m3u"):
            with open("base.m3u", "r") as f:
                data = f.read().replace("{USERNAME}", user).replace("{PASSWORD}", pw)
            with open("final.m3u", "w") as f:
                f.write(data)
            print("📦 final.m3u updated.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_scraper()
