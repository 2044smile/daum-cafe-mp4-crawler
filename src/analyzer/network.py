"""Network request capture and analysis"""
import time
from selenium.webdriver.common.by import By


class NetworkAnalyzer:
    """Analyzes network requests from browser"""
    
    def __init__(self, driver):
        """
        Args:
            driver: WebDriver instance with seleniumwire
        """
        self.driver = driver
    
    def capture_requests(self, initial_count):
        """
        Capture new network requests since initial count
        
        Args:
            initial_count: Starting request count
            
        Returns:
            list: New network requests
        """
        #* [initial_count:]  # 현재 게시글 들어가기 전 count 는 생략 후 새로운 것들만 확인
        new_requests = self.driver.requests[initial_count:]
        print(f"New network requests: {len(new_requests)}")
        
        if len(new_requests) == 0:
            print("WARNING: No network requests captured!")
            print(f"Total requests: {len(self.driver.requests)}")
        else:
            print("Network requests captured successfully!")
            self._preview_requests(new_requests)
        
        return new_requests
    
    def _preview_requests(self, requests, limit=5):
        """Preview captured requests"""
        print("Captured request preview:")
        for i, req in enumerate(requests[:limit]):
            try:
                domain = req.url.split('/')[2] if '://' in req.url else req.url[:50]
                print(f"   [{i+1}] {domain}")
            except:
                print(f"   [{i+1}] {req.url[:50]}...")
        if len(requests) > limit:
            print(f"   ... and {len(requests)-limit} more")
    
    def trigger_video_elements(self):
        """Trigger video elements to load network streams"""
        print("Triggering video elements...")
        try:
            # Find video elements
            videos = self.driver.find_elements(By.TAG_NAME, "video")
            print(f"  Found {len(videos)} video elements")
            
            # Find iframes
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"  Found {len(iframes)} iframes")
            
            # Try to play videos
            for i, video in enumerate(videos):
                try:
                    self.driver.execute_script("arguments[0].play();", video)
                    print(f"    Attempted to play video {i+1}")
                    time.sleep(2)
                except:
                    pass
        
        except Exception as e:
            print(f"  Video trigger error: {e}")
    
    def wait_for_kamp_requests(self, initial_count, max_retries=5):
        """
        Wait for kamp.daum.net requests to complete
        
        Args:
            initial_count: Initial request count
            max_retries: Maximum retry attempts
        """
        print("Waiting for kamp requests...")
        for retry in range(max_retries):
            kamp_count = sum(
                1 for req in self.driver.requests[initial_count:]
                if 'kamp.daum.net' in req.url.lower()
            )
            if kamp_count > 0:
                print(f"  Found {kamp_count} kamp requests, waiting for response...")
                time.sleep(3)
                break
            else:
                print(f"  Waiting for kamp requests... ({retry+1}/{max_retries})")
                time.sleep(2)
    
    def get_initial_request_count(self):
        """Get current request count"""
        count = len(self.driver.requests)
        print(f"Initial network requests: {count}")
        return count
