"""Post extraction utilities"""
from selenium.webdriver.common.by import By
from config.settings import DaumCafeConfig


def extract_post_url_and_title(row):
    """
    Extract URL and title from post row
    
    Args:
        row: Selenium WebElement representing a table row
        
    Returns:
        tuple: (url, title) or (None, None) if extraction fails
    """
    try:
        title_cell = None
        
        # Try various selectors to find title cell
        for selector in DaumCafeConfig.TITLE_SELECTORS:
            try:
                title_cell = row.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        if not title_cell:
            # Find any td with a link
            tds = row.find_elements(By.TAG_NAME, "td")
            for td in tds:
                links = td.find_elements(By.TAG_NAME, "a")
                if links:
                    title_cell = td
                    break
        
        if title_cell:
            # Find link
            link_elements = title_cell.find_elements(By.TAG_NAME, "a")
            for link in link_elements:
                href = link.get_attribute('href')
                title = link.text.strip()
                
                if href and title and len(title) > 2:
                    # Validate post URL pattern
                    is_valid_link = any(
                        pattern in href.lower() 
                        for pattern in DaumCafeConfig.VALID_URL_PATTERNS
                    )
                    
                    if is_valid_link:
                        return href, title
    
    except Exception as e:
        print(f"Error extracting post URL: {e}")
    
    return None, None
