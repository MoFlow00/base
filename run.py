import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import zipfile

def extract_profile():
    """فك ضغط الملف التعريفي إذا لم يكن موجوداً"""
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    zip_path = os.path.join(os.getcwd(), "profile_minimal.zip")
    
    # إذا كان المجلد غير موجود، فك الضغط
    if not os.path.exists(profile_path) and os.path.exists(zip_path):
        print("📦 فك ضغط الملف التعريفي...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        print("✅ تم فك الضغط.")
    return profile_path

def get_account():
    # 1. فك الضغط إذا لزم الأمر
    profile_path = extract_profile()
    
    # 2. إعدادات المتصفح
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = uc.Chrome(options=options, version_main=149)
    
    try:
        driver.get("https://freeiptv2023-d.ottc.xyz/index.php")
        print("✅ الصفحة تحمّلت.")
        
        # الزر سيكون مفعلاً فوراً (لأن الجلسة محفوظة)
        wait = WebDriverWait(driver, 30)
        create_btn = wait.until(EC.element_to_be_clickable((By.ID, "create-btn")))
        create_btn.click()
        print("✅ تم الضغط على الزر.")
        
        # انتظر بيانات الحساب
        wait.until(EC.presence_of_element_located((By.ID, "accUser")))
        print("📋 بيانات الحساب محمّلة.")
        
        # استخراج البيانات
        username = driver.find_element(By.ID, "accUser").get_attribute("value")
        password = driver.find_element(By.ID, "accPass").get_attribute("value")
        server = driver.find_element(By.ID, "serverUrl").get_attribute("value")
        m3u = driver.find_element(By.ID, "m3uLink").get_attribute("value")
        activation = driver.find_element(By.ID, "accAct").get_attribute("value")
        expiration = driver.find_element(By.ID, "accExp").get_attribute("value")
        
        with open("iptv_account.txt", "w") as f:
            f.write(f"Server: {server}\nUsername: {username}\nPassword: {password}\nM3U: {m3u}\nActivation: {activation}\nExpiration: {expiration}")
        
        print("💾 تم الحفظ في iptv_account.txt")
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        driver.save_screenshot("error.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    get_account()
