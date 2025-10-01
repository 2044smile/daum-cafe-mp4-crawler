import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 기본 설정
BASE_DIR = Path(__file__).parent.parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

class SeleniumConfig:
    """Selenium 관련 설정"""
    CHROME_OPTIONS = [
        '--disable-web-security',
        '--allow-running-insecure-content',
        '--disable-features=VizDisplayCompositor',
        '--no-sandbox',  # Linux에서 필요할 수 있음
        '--disable-dev-shm-usage'  # 메모리 문제 방지
    ]

    SELENIUMWIRE_OPTIONS = {
        'addr': '127.0.0.1',
        'port': 0,
        'auto_config': True,
        'suppress_connection_errors': True,
        'verify_ssl': False,
        'connection_timeout': 30,
        'read_timeout': 30,
    }

    IMPLICIT_WAIT = 10
    PAGE_LOAD_TIMEOUT = 30

class DaumCafeConfig:
    """Daum 카페 크롤링 설정"""
    KAKAO_ID = os.getenv('KAKAO_ID')
    KAKAO_PASSWORD = os.getenv('KAKAO_PASSWORD')
    LOGIN_URL = os.getenv('LOGIN_URL')
    TARGET_CAFE_URL = os.getenv('TARGET_CAFE_URL')

    # 게시글 제목 추출 선택자
    TITLE_SELECTORS = [
        ".td_title",
        ".title",
        "td.title",
        "td:nth-child(3)",
        "td:nth-child(4)"
    ]

    # 게시글 목록 선택자
    POST_ROW_SELECTORS = [
        "#article-list tbody tr:not(.state_info)",
        "#article-list tbody tr",
        "#article-list tr:not(.state_info)",
        "#article-list tr",
    ]

    # 페이지네이션 선택자
    PAGE_SELECTORS = [
        "a.link_num span.num_item",
        "a[href*='javascript:'] span",
        "a[href*='page'] span",
    ]

    # iframe 후보
    IFRAME_CANDIDATES = ["down"]

    # 유효한 게시글 URL 패턴
    VALID_URL_PATTERNS = ['bbs_read', 'read', 'view', 'article']

    # 비디오 도메인
    VIDEO_DOMAINS = [
        'play.daum.net',
        'kdnv-skb-orisa-edge.play.daum.net',
        'kamp.daum.net'
    ]

    # 대기 시간 설정
    LOGIN_DELAY = 5
    PAGE_LOAD_DELAY = 3
    VIDEO_TRIGGER_DELAY = 8
    IFRAME_SWITCH_DELAY = 2

class DownloadConfig:
    """다운로드 관련 설정"""
    VIDEO_EXTENSIONS = ['.mp4']  # '.webm', '.avi', '.mov', '.flv'
    PREFERRED_QUALITIES = ['480p']  # '720p', '1080p', '360p'
    CHUNK_SIZE = 8192
    DOWNLOAD_TIMEOUT = 30
    MAX_RETRIES = 3

class LogConfig:
    """로그 관련 설정"""
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    SAVE_TO_FILE = True
    LOG_FILE = BASE_DIR / "logs" / "crawler.log"
