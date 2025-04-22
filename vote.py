from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
import undetected_chromedriver as uc
import os
import time
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor

# ==== CẤU HÌNH ====
CLASS_NAME = "IC1752"
CHROME_DRIVER_PATH = os.path.join(os.getcwd(), "chromedriver-win64", "chromedriver.exe")
VOTE_URL = "https://momentum.izone.edu.vn/#vote-gallery"
ACCOUNT_FILE = "accounts.txt"
LOOP_INTERVAL_SECONDS = 30

# ==== TẢI TẤT CẢ TÀI KHOẢN ====
def load_all_accounts(filepath=ACCOUNT_FILE):
    if not os.path.exists(filepath):
        print(f"❌ Không tìm thấy file {filepath}")
        return []
    accounts = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if "|" in line:
                email, password = line.strip().split("|")
                accounts.append((email.strip(), password.strip()))
    return accounts

# ==== DRIVER ====
def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1200,800")
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2,
        "profile.managed_default_content_settings.fonts": 2
    }
    options.add_experimental_option("prefs", prefs)
    driver = uc.Chrome(service=Service(CHROME_DRIVER_PATH), options=options)
    driver.set_window_size(1200, 600)
    return driver

# ==== ĐĂNG NHẬP ====
def login(driver, email, password):
    try:
        print("🌐 Truy cập trang...")
        driver.get(VOTE_URL)
        time.sleep(0.5)

        print("🔐 Tìm nút đăng nhập...")
        login_btn_xpath = "//*[self::button or self::a or self::div][contains(text(), 'Đăng nhập')]"
        login_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, login_btn_xpath))
        )
        login_btn.click()

        print("⌛ Chờ form đăng nhập...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @type='text']"))
        )

        print(f"👤 Nhập tài khoản: {email}")
        driver.find_element(By.XPATH, "//input[@type='email' or @type='text']").send_keys(email)
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys(password)

        print("🚪 Nhấn nút Đăng nhập...")
        driver.find_element(By.ID, "kc-login").click()

        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(0.5)
        print("✅ Đăng nhập thành công.")
        return True

    except Exception as e:
        print(f"❌ Lỗi đăng nhập: {str(e)}")
        return False

# ==== BÌNH CHỌN ====
def perform_vote(driver):
    try:
        print("\n📨 Truy cập lại trang vote...")
        driver.get(VOTE_URL)
        time.sleep(0.5)

        print("🔍 Tìm và chọn lớp...")
        class_xpath = f"//div[contains(@class, 'course-class-item')]//div[normalize-space(text())='{CLASS_NAME}']/ancestor::div[contains(@class, 'course-class-item')]"
        class_element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, class_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", class_element)
        class_element.click()
        print(f"✅ Đã chọn lớp {CLASS_NAME}")
        time.sleep(0.5)

        vote_button_xpath = "//button[contains(@class, 'text-support-primary') and contains(normalize-space(.), 'Bình')]"
        vote_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, vote_button_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView();", vote_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", vote_button)

        print("🎉 Bình chọn thành công!")
        return True

    except TimeoutException:
        print("❌ Không tìm thấy lớp hoặc nút bình chọn.")
        return False
    except Exception as e:
        print(f"❌ Lỗi khi vote: {str(e)}")
        return False

# ==== XỬ LÝ 1 TÀI KHOẢN ====
def vote_with_account(account):
    email, password = account
    print(f"\n📧 Đang xử lý: {email}")
    driver = get_driver()
    try:
        if login(driver, email, password):
            perform_vote(driver)
    finally:
        driver.quit()

# ==== CHIA NHÓM ====
def chunk_accounts(accounts, size=3):
    for i in range(0, len(accounts), size):
        yield accounts[i:i + size]

# ==== MAIN LOOP ====
def main():
    accounts = load_all_accounts()
    if not accounts:
        print("⚠️ Không có tài khoản.")
        return

    while True:
        for group in chunk_accounts(accounts, 3):
            with ThreadPoolExecutor(max_workers=3) as executor:
                executor.map(vote_with_account, group)
        print(f"⏳ Đợi {LOOP_INTERVAL_SECONDS} giây trước khi lặp lại...\n")
        time.sleep(LOOP_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()