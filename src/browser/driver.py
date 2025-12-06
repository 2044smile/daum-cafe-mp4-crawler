"""Browser driver initialization and configuration"""
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import SeleniumConfig


def create_driver():
    """
    Create Chrome driver with Selenium Wire

    Returns:
        webdriver: Configured Chrome WebDriver instance
    """
    service = Service(ChromeDriverManager().install())
    options = Options()

    # Add Chrome options
    for option in SeleniumConfig.CHROME_OPTIONS:
        options.add_argument(option)

    seleniumwire_options = SeleniumConfig.SELENIUMWIRE_OPTIONS

    print("Setting up seleniumwire proxy...")

    # Create Chrome driver
    driver = webdriver.Chrome(
        service=service,
        options=options,
        seleniumwire_options=seleniumwire_options
    )

    print(f"Seleniumwire proxy activated: {driver.proxy}")
    print("All network requests will now be captured!")

    return driver


def create_wait(driver, timeout=10):
    """
    Create WebDriverWait object

    Args:
        driver: WebDriver instance
        timeout: Wait timeout in seconds

    Returns:
        WebDriverWait: Wait object
    """
    return WebDriverWait(driver, timeout)
