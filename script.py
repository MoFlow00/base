import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

def get_account():
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = uc.Chrome(options=options)
    try:
        driver.get("https://freeiptv2023-d.ottc.xyz/index.php")
        print("Page loaded. Waiting for button to become enabled...")

        wait = WebDriverWait(driver, 120)
        create_btn = wait.until(EC.element_to_be_clickable((By.ID, "create-btn")))
        create_btn.click()
        print("Button clicked!")

        wait.until(EC.presence_of_element_located((By.ID, "accUser")))
        print("Account info loaded.")

        username = driver.find_element(By.ID, "accUser").get_attribute("value")
        password = driver.find_element(By.ID, "accPass").get_attribute("value")
        server = driver.find_element(By.ID, "serverUrl").get_attribute("value")
        m3u = driver.find_element(By.ID, "m3uLink").get_attribute("value")
        activation = driver.find_element(By.ID, "accAct").get_attribute("value")
        expiration = driver.find_element(By.ID, "accExp").get_attribute("value")

        with open("iptv_account.txt", "w") as f:
            f.write(f"Server URL: {server}\nUsername: {username}\nPassword: {password}\nM3U: {m3u}\nActivation: {activation}\nExpiration: {expiration}\n")

        print("Credentials saved.")

    except Exception as e:
        print(f"Error: {e}")
        driver.save_screenshot("error.png")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
    finally:
        driver.quit()

if __name__ == "__main__":
    get_account()
