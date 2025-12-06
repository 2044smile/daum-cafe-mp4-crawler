"""Stream URL parser from network requests"""
import json
import gzip
import re
from config.settings import DaumCafeConfig


class StreamParser:
    """Parses stream URLs from network requests"""
    
    def __init__(self):
        self.download_targets = []
    
    def parse_requests(self, requests):
        """
        Parse network requests to find video stream URLs
        
        Args:
            requests: List of network requests
            
        Returns:
            list: List of download URLs
        """
        print("\nAnalyzing stream files...")
        print("=" * 50)
        
        mp4_files = []
        hls_files = []
        dash_files = []
        other_video_files = []
        kamp_requests = []
        self.download_targets = []
        
        # Classify requests by type
        for i, request in enumerate(requests):
            try:
                url = request.url.lower()
                
                if 'kamp.daum.net' in url:
                    kamp_requests.append(request)
                    print(f"  Found kamp request: {request.url}")
                
                elif '.mp4' in url:
                    mp4_files.append(request)
                    if '480p' in url:
                        print(f"  Found 480p MP4: {request.url}")
                    else:
                        print(f"  Found MP4 file: {request.url}")
                
                elif '.m3u8' in url or '.ts' in url:
                    hls_files.append(request)
                    print(f"  Found HLS file: {request.url}")
                
                elif '.mpd' in url or '.m4s' in url:
                    dash_files.append(request)
                    print(f"  Found DASH file: {request.url}")
                
                elif any(ext in url for ext in ['.webm', '.avi', '.mov', '.flv']):
                    other_video_files.append(request)
                    print(f"  Found other video: {request.url}")
            
            except Exception as e:
                print(f"  Error analyzing request [{i}]: {e}")
        
        # Print summary
        print(f"\nStream file analysis result:")
        print("=" * 50)
        print(f"  Kamp requests: {len(kamp_requests)}")
        print(f"  MP4 files: {len(mp4_files)}")
        print(f"  HLS files: {len(hls_files)}")
        print(f"  DASH files: {len(dash_files)}")
        print(f"  Other videos: {len(other_video_files)}")
        
        # Parse kamp requests
        if kamp_requests:
            self._parse_kamp_requests(kamp_requests)
        
        # Search all requests for Daum video URLs
        self._search_daum_video_urls(requests)
        
        # Find 480p from regular MP4 requests
        for request in mp4_files:
            url = request.url
            if '480p' in url.lower() and url not in self.download_targets:
                self.download_targets.append(url)
                print(f"  Found 480p in regular request: {url}")
        
        # Print final targets
        self._print_final_targets(mp4_files)
        
        return self.download_targets
    
    def _parse_kamp_requests(self, kamp_requests):
        """Parse kamp.daum.net requests for stream data"""
        print(f"\nExtracting streams data from kamp requests...")
        for i, request in enumerate(kamp_requests):
            try:
                print(f"  Checking kamp [{i+1}] request status...")
                print(f"     URL: {request.url}")
                print(f"     Has response: {request.response is not None}")
                
                if request.response:
                    print(f"     Status code: {request.response.status_code}")
                    print(f"     Has body: {request.response.body is not None}")
                
                if request.response and request.response.body:
                    body = self._decompress_response(request.response)
                    
                    print(f"  kamp [{i+1}] response size: {len(body)} bytes")
                    print(f"  Response preview (first 500 chars): {body[:500]}...")
                    print(f"  Contains 'streams': {'streams' in body}")
                    print(f"  Contains 'mp4': {'mp4' in body}")
                    print(f"  Contains '480': {'480' in body}")
                    
                    if 'streams' in body:
                        print(f"  Found streams data in kamp request [{i+1}]!")
                        self._parse_streams_json(body, i)
                    else:
                        print(f"  No streams data in kamp request [{i+1}]")
            
            except Exception as e:
                print(f"  Error analyzing kamp request [{i+1}]: {e}")
    
    def _decompress_response(self, response):
        """Decompress gzip response if needed"""
        raw_body = response.body
        
        try:
            if response.headers.get('content-encoding') == 'gzip':
                body = gzip.decompress(raw_body).decode('utf-8', errors='ignore')
                print(f"  Gzip decompression successful!")
            else:
                body = raw_body.decode('utf-8', errors='ignore')
        except Exception as decompress_error:
            print(f"  Decompression failed: {decompress_error}")
            try:
                body = raw_body.decode('utf-8', errors='ignore')
            except:
                body = str(raw_body)
        
        return body
    
    def _parse_streams_json(self, body, request_index):
        """Parse JSON streams data"""
        try:
            data = json.loads(body)
            
            if 'streams' in data:
                streams = data['streams']
                print(f"    Streams data type: {type(streams)}")
                print(f"    Streams content: {streams}")
                
                if isinstance(streams, list):
                    self._parse_streams_list(streams)
                elif isinstance(streams, dict):
                    self._parse_streams_dict(streams)
        
        except json.JSONDecodeError:
            print(f"    JSON parsing failed, searching raw data for streams")
            self._parse_streams_raw(body)
    
    def _parse_streams_list(self, streams):
        """Parse streams array"""
        print(f"    Searching for 480p MP4 in streams array (total {len(streams)}):")
        for j, stream in enumerate(streams):
            if isinstance(stream, dict):
                name = stream.get('name', '')
                protocol = stream.get('protocol', '')
                url = stream.get('url', '')
                status = stream.get('status', '')
                
                print(f"      [{j+1}] name='{name}', protocol='{protocol}', status='{status}'")
                print(f"           URL: {url[:80]}..." if url else "           URL: None")
                
                # Match: name="480p" AND protocol="mp4"
                if name == '480p' and protocol == 'mp4' and url:
                    print(f"      Exact 480p MP4 stream found!")
                    self.download_targets.append(url)
                # Backup: 480p in name and .mp4 in URL
                elif '480' in name.lower() and url and '.mp4' in url.lower():
                    print(f"      Found 480p MP4 pattern!")
                    self.download_targets.append(url)
                # Additional: 480P pattern in URL
                elif url and ('480p' in url.lower() or '480P' in url) and '.mp4' in url.lower():
                    print(f"      Found 480P MP4 pattern in URL!")
                    self.download_targets.append(url)
    
    def _parse_streams_dict(self, streams):
        """Parse streams dictionary"""
        print(f"    Searching for 480p in streams dictionary:")
        for quality, stream_data in streams.items():
            print(f"      Quality: '{quality}'")
            
            if '480' in quality.lower():
                if isinstance(stream_data, str):
                    print(f"      480p URL: {stream_data}")
                    self.download_targets.append(stream_data)
                elif isinstance(stream_data, dict) and 'url' in stream_data:
                    url = stream_data['url']
                    print(f"      480p URL: {url}")
                    self.download_targets.append(url)
    
    def _parse_streams_raw(self, body):
        """Parse raw text for 480p URLs"""
        mp4_pattern = r'https?://[^\s"\']+480[pP][^\s"\']*\.mp4[^\s"\']*'
        matches = re.findall(mp4_pattern, body)
        
        if matches:
            print(f"    Found {len(matches)} 480p MP4 URLs in raw data")
            for match in matches:
                print(f"      {match}")
                self.download_targets.append(match)
    
    def _search_daum_video_urls(self, requests):
        """Search all requests for Daum video URLs"""
        print(f"\nSearching for Daum video URLs in all requests...")
        for request in requests:
            try:
                url = request.url
                url_lower = url.lower()
                
                # Daum video domain + MP4 + 480P pattern
                if any(domain in url_lower for domain in DaumCafeConfig.VIDEO_DOMAINS) and '.mp4' in url_lower:
                    # Check for 480P
                    if '480p' in url_lower or '480P' in url:
                        if url not in self.download_targets:
                            self.download_targets.append(url)
                            print(f"  Found Daum 480P MP4: {url}")
                
                # URLs with orisa-token
                elif 'orisa-token' in url_lower and '.mp4' in url_lower:
                    if url not in self.download_targets:
                        self.download_targets.append(url)
                        print(f"  Found orisa-token MP4: {url}")
            
            except Exception as e:
                continue
    
    def _print_final_targets(self, mp4_files):
        """Print final download targets"""
        print(f"\nFinal download targets:")
        print("=" * 50)
        
        if self.download_targets:
            for i, url in enumerate(self.download_targets, 1):
                print(f"  [{i}] {url}")
        else:
            print(f"  WARNING: No 480p MP4 files found.")
            
            if mp4_files:
                print(f"\nOther quality MP4 files found:")
                for request in mp4_files:
                    url = request.url
                    print(f"    {url}")
