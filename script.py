import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def get_account():
    # تأكد من إصدار Chrome الموجود في الرانر (149 حالياً)
    # لو تغير في المستقبل، غيّر الرقم أو اتركه بدون تحديد
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')

    # تحديد الإصدار الرئيسي ليتطابق مع Chrome 149
    driver = uc.Chrome(options=options, version_main=149)

    try:
        print("1️⃣ جارٍ تحميل الصفحة...")
        driver.get("https://freeiptv2023-d.ottc.xyz/index.php")
        driver.save_screenshot("1_page_loaded.png")
        print("✅ تم تحميل الصفحة (تم حفظ لقطة: 1_page_loaded.png)")

        # ننتظر قليلاً لنرى هل تظهر الكابتشا (لكننا لن نحلها)
        print("2️⃣ في انتظار تفعيل الزر (كابتشا غير محلولة)...")
        wait = WebDriverWait(driver, 30)  # 30 ثانية فقط للتجربة
        create_btn = wait.until(EC.element_to_be_clickable((By.ID, "create-btn")))
        create_btn.click()
        print("✅ تم الضغط على الزر (غير متوقع أن يحدث)")

        # لو حدث وضغطنا، ننتظر بيانات الحساب
        wait.until(EC.presence_of_element_located((By.ID, "accUser")))
        print("✅ تم تحميل بيانات الحساب.")

        # استخراج البيانات
        username = driver.find_element(By.ID, "accUser").get_attribute("value")
        password = driver.find_element(By.ID, "accPass").get_attribute("value")
        server = driver.find_element(By.ID, "serverUrl").get_attribute("value")
        m3u = driver.find_element(By.ID, "m3uLink").get_attribute("value")
        activation = driver.find_element(By.ID, "accAct").get_attribute("value")
        expiration = driver.find_element(By.ID, "accExp").get_attribute("value")

        with open("iptv_account.txt", "w") as f:
            f.write(f"Server URL: {server}\nUsername: {username}\nPassword: {password}\nM3U: {m3u}\nActivation: {activation}\nExpiration: {expiration}\n")
        print("💾 تم حفظ البيانات في iptv_account.txt")

    except Exception as e:
        print(f"❌ حدث خطأ (كما هو متوقع بسبب الكابتشا): {e}")
        driver.save_screenshot("2_error.png")
        with open("3_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("📸 تم حفظ لقطة للخطأ ومصدر الصفحة.")

    finally:
        driver.quit()
        print("🏁 تم إغلاق المتصفح.")

if __name__ == "__main__":
    get_account()
