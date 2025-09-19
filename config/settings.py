import os
from pathlib import Path
from dotenv import load_dotenv


# 프로젝트 루트 경로
BASE_DIR = Path(__file__).parent.parent

# .env 파일 로드
load_dotenv(BASE_DIR / ".env")

class Settings:

    def __init__(self):
        self._validate_env_vars()

        # 카카오 로그인 설정
        self.KAKAO_ID = os.getenv('KAKAO_ID')
        self.KAKAO_PASSWORD = os.getenv('KAKAO_PASSWORD')
        self.LOGIN_URL = os.getenv('LOGIN_URL')

        # 카페 설정
        self.DAUM_CAFE_URL = os.getenv('DAUM_CAFE_URL', 'https://cafe.daum.net')
        self.TARGET_CAFE_URL = os.getenv('TARGET_CAFE_URL')
        self.BOARD_IDS = os.getenv('BOARD_IDS', [])

        # 크롤링 설정
        self.WAIT_TIMEOUT = int(os.getenv('WAIT_TIMEOUT', '10'))
        self.REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))

        # 디렉토리 설정
        self.BASE_DIR = BASE_DIR
        self.DOWNLOADS_DIR = BASE_DIR / "downloads"
        self.LOGS_DIR = BASE_DIR / "logs"

        # 디렉토리 생성
        self._create_directories()


    def _validate_env_vars(self):
        """환경변수 검증"""
        required_vars = ['KAKAO_ID', 'KAKAO_PASSWORD', 'TARGET_CAFE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(f"필수 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        
    def _create_directories(self):
        """디렉토리 생성"""
        self.DOWNLOADS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)

    def _parse_board_ids(self, board_ids_str):
        """BOARD_IDS 문자열을 리스트로 파싱"""
        if not board_ids_str:
            return []
        
        if isinstance(board_ids_str, str):
            # 쉼표, 세미골론, 공백으로 구분 가능
            import re
            board_ids = re.split(r'[,;\s]+', board_ids_str.strip())
            return [board_id.strip() for board_id in board_ids if board_id.strip()]
        
        return board_ids_str

# 전역 설정 인스턴스
settings = Settings()

def get_settings():
    """설정 인스턴스 반환"""
    return settings
