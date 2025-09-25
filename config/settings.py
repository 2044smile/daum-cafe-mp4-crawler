import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

class Settings:
    KAKAO_ID = os.getenv('KAKAO_ID')
    KAKAO_PASSWORD = os.getenv('KAKAO_PASSWORD')
    LOGIN_URL = os.getenv('LOGIN_URL')  # 추후에 daum, naver, etc... 확장
    TARGET_CAFE_URL = os.getenv('TARGET_CAFE_URL')

    DOWNLOAD_DIR = Path("downloads")  # 현재 경로에 폴더를 생성

    # 현재 하드코딩된 값들을 설정으로 이동
    # TITLE_SELECTORS = [".td_title", ".title", "td.title", "td:nth-child(3)", "td:nth-child(4)"]
    # VALID_PATTERNS = ['bbs_read', 'read', 'view', 'article']
    # DAUM_DOMAINS = ['play.daum.net', 'kdnv-skb-orisa-edge.play.daum.net', 'kamp.daum.net']
    
    # 시간 설정들 (현재 하드코딩된 값들)
    PAGE_LOAD_TIMEOUT = 10
    VIDEO_TRIGGER_DELAY = 8
    LOGIN_DELAY = 5
