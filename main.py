"""
Daum Cafe MP4 Crawler
Downloads MP4 videos from Daum Cafe boards
"""
import time
from selenium.webdriver.common.by import By

from config.settings import DaumCafeConfig
from src.browser import create_driver, Navigator
from src.auth import login_to_kakao
from src.scraper import BoardScraper, Paginator, extract_post_url_and_title
from src.downloader import VideoDownloader


def main():
    """Main entry point"""
    # Initialize browser
    driver = create_driver()
    navigator = Navigator(driver)
    
    try:
        # Login
        print("\n" + "="*60)
        print("STEP 1: Login")
        print("="*60)
        login_to_kakao(driver)
        
        # Navigate to cafe
        print("\n" + "="*60)
        print("STEP 2: Navigate to Cafe")
        print("="*60)
        time.sleep(5)
        navigator.goto(DaumCafeConfig.TARGET_CAFE_URL, delay=5)
        
        # Navigate to specific board
        board_url = f"{DaumCafeConfig.TARGET_CAFE_URL}/WZbj"
        navigator.goto(board_url, delay=5)
        print(f"Current URL: {navigator.get_current_url()}")
        
        # Find and switch to board iframe
        print("\n" + "="*60)
        print("STEP 3: Find Board Frame")
        print("="*60)
        navigator.find_and_switch_to_board_iframe(DaumCafeConfig.IFRAME_CANDIDATES)
        print("Iframe processing complete")
        time.sleep(2)
        
        # Initialize scrapers and downloader
        board_scraper = BoardScraper(driver)
        paginator = Paginator(driver)
        downloader = VideoDownloader(driver)
        
        # Get initial posts
        post_rows = board_scraper.get_post_rows()
        
        if not post_rows:
            print("No posts found. Exiting.")
            return
        
        # Process all pages
        print("\n" + "="*60)
        print("STEP 4: Process All Pages")
        print("="*60)
        
        page_num = 1
        while True:
            print(f"\n{'='*60}")
            print(f"Processing page {page_num}...")
            print(f"{'='*60}")
            
            # Navigate to page (skip for first page)
            if page_num > 1:
                if not paginator.goto_page(page_num):
                    print(f"Could not navigate to page {page_num}. Stopping.")
                    break
            
            # Get posts on current page
            current_post_rows = board_scraper.get_post_rows()
            
            if not current_post_rows:
                print(f"No posts found on page {page_num}")
                page_num += 1
                continue
            
            # Collect all post URLs and titles
            print(f"  Collecting all post URLs from page {page_num}...")
            post_data_list = []
            
            for i, row in enumerate(current_post_rows):
                try:
                    post_url, post_title = extract_post_url_and_title(row)
                    if post_url and post_title:
                        post_data_list.append((post_url, post_title))
                        print(f"    [{page_num}-{i+1}] {post_title[:50]}...")
                    else:
                        print(f"    [{page_num}-{i+1}] URL extraction failed")
                except Exception as e:
                    print(f"    [{page_num}-{i+1}] URL collection error: {e}")
            
            print(f"  Collected {len(post_data_list)} post URLs from page {page_num}")
            
            # Process collected posts
            for i, (post_url, post_title) in enumerate(post_data_list, 1):
                try:
                    print(f"\n  [{page_num}-{i}] Processing post...")
                    print(f"    Title: {post_title[:50]}...")
                    print(f"    URL: {post_url}")
                    
                    # Analyze and download
                    downloader.analyze_and_download(post_url, f"[{page_num}-{i}]{post_title}")
                    
                    # Go back to board
                    print(f"    Returning to board...")
                    navigator.back(delay=2)
                    
                    # Re-enter iframe
                    try:
                        navigator.switch_to_iframe("down")
                        time.sleep(1)
                    except:
                        print(f"    Warning: iframe re-entry failed")
                
                except Exception as e:
                    print(f"    Error processing post [{page_num}-{i}]: {e}")
                    # Try to return to board
                    try:
                        navigator.back(delay=2)
                        navigator.switch_to_iframe("down")
                    except:
                        pass
            
            print(f"\nCompleted page {page_num}")
            
            # Check if next page exists
            if not paginator.has_next_page(page_num):
                print(f"\nReached last page ({page_num})")
                break
            
            page_num += 1
        
        print(f"\n{'='*60}")
        print(f"All pages processed (total {page_num} pages)!")
        print(f"{'='*60}")
    
    finally:
        # Cleanup
        print("\nClosing browser...")
        driver.quit()
        print("Done!")


if __name__ == "__main__":
    main()
