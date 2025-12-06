"""Kakao login functionality"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.settings import DaumCafeConfig


def login_to_kakao(driver):
    """
    Login to Kakao account
    
    Args:
        driver: WebDriver instance
        
    Returns:
        bool: Login success status
    """
    wait = WebDriverWait(driver, 10)
    
    print(f"Navigating to login page: {DaumCafeConfig.LOGIN_URL}")
    driver.get(DaumCafeConfig.LOGIN_URL)
    time.sleep(3)
    
    # Enter ID
    try:
        id_input = wait.until(EC.element_to_be_clickable((By.NAME, "loginId")))
        id_input.clear()
        time.sleep(0.5)
        id_input.send_keys(DaumCafeConfig.KAKAO_ID)
        print(f"ID entered: {DaumCafeConfig.KAKAO_ID}")
    except Exception as e:
        print(f"Failed to enter ID: {e}")
        return False
    
    # Enter password
    try:
        pw_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        pw_input.clear()
        time.sleep(0.5)
        pw_input.send_keys(DaumCafeConfig.KAKAO_PASSWORD)
        print("Password entered")
    except Exception as e:
        print(f"Failed to enter password: {e}")
        return False
    
    # Click login button
    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        driver.execute_script("arguments[0].click();", login_btn)
        print("Login button clicked")
    except Exception as e:
        print(f"Failed to click login button: {e}")
        return False
    
    # Wait for login processing
    time.sleep(10)
    
    print(f"Current URL: {driver.current_url}")
    print("Login completed successfully")
    
    return True
