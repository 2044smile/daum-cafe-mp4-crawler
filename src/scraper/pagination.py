"""Pagination handling"""
import time
from selenium.webdriver.common.by import By
from config.settings import DaumCafeConfig


class Paginator:
    """Handles pagination for board pages"""
    
    def __init__(self, driver):
        """
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
    
    def goto_page(self, page_num):
        """
        Navigate to specific page number
        
        Args:
            page_num: Page number to navigate to
            
        Returns:
            bool: Success status
        """
        try:
            print(f"Navigating to page {page_num}...")
            
            # Try to find page number link
            for selector in DaumCafeConfig.PAGE_SELECTORS:
                try:
                    page_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in page_elements:
                        if element.text.strip() == str(page_num):
                            page_button = element.find_element(By.XPATH, "..")
                            page_button.click()
                            print(f"  Successfully clicked page {page_num}")
                            time.sleep(3)
                            return True
                except:
                    continue
            
            print(f"  Could not find page {page_num} button")
            return False
            
        except Exception as e:
            print(f"  Failed to navigate to page {page_num}: {e}")
            return False
    
    def has_next_page(self, current_page):
        """
        Check if next page exists
        
        Args:
            current_page: Current page number
            
        Returns:
            bool: True if next page exists
        """
        next_page_num = current_page + 1
        
        try:
            # Check if next page number exists
            page_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "a.link_num span.num_item"
            )
            for element in page_elements:
                if element.text.strip() == str(next_page_num):
                    return True
            
            # Check for next button
            next_button_selectors = [
                "a.link_next",
                "a[href*='javascript:'][title*='next']",
                "a[href*='javascript:']"
            ]
            
            for selector in next_button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        button_text = button.text.strip()
                        if ('next' in button_text.lower() or '>' in button_text) and button.is_enabled():
                            return True
                except:
                    continue
            
        except Exception as e:
            print(f"  Error checking next page: {e}")
        
        return False
