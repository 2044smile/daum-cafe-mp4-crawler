"""Video download functionality"""
import time
import requests
from pathlib import Path

from config.settings import DOWNLOAD_DIR, DaumCafeConfig, DownloadConfig
from .filename import sanitize_filename
from ..analyzer.network import NetworkAnalyzer
from ..analyzer.stream_parser import StreamParser


class VideoDownloader:
    """Downloads videos from analyzed network requests"""
    
    def __init__(self, driver):
        """
        Args:
            driver: WebDriver instance
        """
        self.driver = driver
        self.network_analyzer = NetworkAnalyzer(driver)
        self.stream_parser = StreamParser()
    
    def analyze_and_download(self, post_url, post_title):
        """
        Analyze post and download videos
        
        Args:
            post_url: Post URL
            post_title: Post title
        """
        print(f"\n{'='*60}")
        print(f"Analyzing post stream: {post_title}...")
        print(f"{'='*60}")
        
        try:
            # Get initial request count
            initial_request_count = self.network_analyzer.get_initial_request_count()
            
            # Navigate to post
            print(f"Navigating to post...")
            self.driver.get(post_url)
            time.sleep(5)
            
            # Trigger video elements
            self.network_analyzer.trigger_video_elements()
            
            # Wait for network streams to load
            print(f"Waiting for network streams to load...")
            time.sleep(8)
            
            # Wait for kamp requests
            self.network_analyzer.wait_for_kamp_requests(initial_request_count)
            
            # Capture new requests
            new_requests = self.network_analyzer.capture_requests(initial_request_count)
            
            # Parse streams
            download_targets = self.stream_parser.parse_requests(new_requests)
            
            # Download 480p MP4 files
            if download_targets:
                print(f"\nStarting 480p MP4 downloads...")
                print(f"\nUsing simple requests download...")
                
                success_count = 0
                
                for i, url in enumerate(download_targets, 1):
                    try:
                        print(f"\n[{i}/{len(download_targets)}] Downloading...")
                        print(f"URL: {url[:80]}...")
                        
                        # Generate filename
                        filename = sanitize_filename(f"{post_title}_{i}_480p.mp4")
                        filepath = DOWNLOAD_DIR / filename
                        
                        print(f"Saving to: {filename}")
                        
                        # Download with streaming
                        with requests.get(url, stream=True, timeout=DownloadConfig.DOWNLOAD_TIMEOUT) as r:
                            r.raise_for_status()
                            
                            total_size = int(r.headers.get('content-length', 0))
                            if total_size > 0:
                                print(f"File size: {total_size / (1024*1024):.2f} MB")
                            
                            downloaded_size = 0
                            
                            with open(filepath, "wb") as f:
                                for chunk in r.iter_content(chunk_size=DownloadConfig.CHUNK_SIZE):
                                    if chunk:
                                        f.write(chunk)
                                        downloaded_size += len(chunk)
                                        
                                        if total_size > 0:
                                            progress = (downloaded_size / total_size) * 100
                                            print(f"\r  Progress: {progress:.1f}%", end='', flush=True)
                        
                        if filepath.exists():
                            file_size = filepath.stat().st_size
                            print(f"\nDownload complete: {file_size / (1024*1024):.2f} MB")
                            success_count += 1
                        
                        time.sleep(1)
                    
                    except Exception as e:
                        print(f"\nDownload failed: {e}")
                
                print(f"\nDownload result: {success_count}/{len(download_targets)} successful")
                
                if success_count == 0:
                    print(f"\nWARNING: All downloads failed. Check URL or network status.")
            
            else:
                print(f"\nNo 480p MP4 files to download.")
        
        except Exception as e:
            print(f"Error analyzing post stream: {e}")
            import traceback
            traceback.print_exc()
