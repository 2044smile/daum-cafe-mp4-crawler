"""Browser navigation utilities"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class Navigator:
    """Handles browser navigation"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def goto(self, url, delay=3):
        """Navigate to URL"""
        self.driver.get(url)
        time.sleep(delay)

    def back(self, delay=2):
        """Go back to previous page"""
        self.driver.back()
        time.sleep(delay)

    def switch_to_iframe(self, iframe_name):
        """Switch to iframe by name or id"""
        try:
            self.driver.switch_to.frame(iframe_name)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"  Failed to switch to iframe '{iframe_name}': {e}")
            return False

    def switch_to_iframe_by_index(self, index):
        """Switch to iframe by index"""
        try:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(index)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"  Failed to switch to iframe index [{index}]: {e}")
            return False

    def switch_to_default(self):
        """Switch to main frame"""
        try:
            self.driver.switch_to.default_content()
        except:
            pass

    def find_and_switch_to_board_iframe(self, iframe_candidates):
        """Find and switch to board iframe"""
        print("Finding iframe...")

        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")

        for i, iframe in enumerate(iframes):
            try:
                iframe_src = iframe.get_attribute("src") or ""
                iframe_id = iframe.get_attribute("id") or ""
                iframe_name = iframe.get_attribute("name") or ""
                print(f"  [{i+1}] iframe - id: '{iframe_id}', name: '{iframe_name}', src: {iframe_src[:100]}...")
            except Exception as e:
                print(f"  [{i+1}] iframe info error: {e}")

        for iframe_name in iframe_candidates:
            try:
                print(f"Trying to switch to iframe '{iframe_name}'...")
                self.driver.switch_to.frame(iframe_name)
                time.sleep(2)

                try:
                    self.driver.find_element(By.ID, "article-list")
                    print(f"Successfully switched to iframe '{iframe_name}'!")
                    return True
                except:
                    print(f"  iframe '{iframe_name}' - no article-list")
                    self.switch_to_default()
            except Exception as e:
                print(f"  Failed to switch iframe '{iframe_name}': {e}")
                self.switch_to_default()

        if len(iframes) > 0:
            for i, iframe in enumerate(iframes):
                try:
                    print(f"Trying iframe index [{i}]...")
                    self.switch_to_default()
                    self.driver.switch_to.frame(i)
                    time.sleep(2)

                    try:
                        self.driver.find_element(By.ID, "article-list")
                        print(f"Successfully switched to iframe index [{i}]!")
                        return True
                    except:
                        print(f"  iframe index [{i}] - no article-list")
                except Exception as e:
                    print(f"  Failed to switch iframe index [{i}]: {e}")
                    self.switch_to_default()

        print("Could not find appropriate iframe. Proceeding with main frame.")
        self.switch_to_default()
        return False

    def get_current_url(self):
        """Get current URL"""
        return self.driver.current_url
