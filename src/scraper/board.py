"""Board scraping functionality"""
from selenium.webdriver.common.by import By
from config.settings import DaumCafeConfig


class BoardScraper:
    """Scrapes board posts from Daum Cafe"""
    
    def __init__(self, driver):
        """
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
    
    def get_post_rows(self):
        """
        Get all post rows from current page
        
        Returns:
            list: List of WebElement rows
        """
        for selector in DaumCafeConfig.POST_ROW_SELECTORS:
            try:
                rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if rows:
                    print(f"  Found {len(rows)} posts (selector: {selector})")
                    return rows
            except:
                continue
        
        print("  No post rows found")
        return []
    
    def wait_for_page_load(self, delay=3):
        """Wait for page to load"""
        import time
        time.sleep(delay)
