# DAUM-CAFE-MP4-CRAWLER

## 라이브러리

### Selenium + selenium-wire

- `selenium`: 웹 브라우저 자동화 (로그인, 클릭, **iframe** 전환 등)
- `selenium-wire`: **브라우저 네트워크 요청 추적 가능**

### webdriver_manager

- 자동으로 크롬 드라이버 다운로드 및 실행 경로 지정
- 개발환경에 따라 크롬 드라이버 버전을 직접 맞추지 않아도 됨

### dotenv

- `.env` 파일을 불러와서 환경 변수 관리

### requests

- Selenium이 아니라 **직접 영상 다운로드**를 위해서 사용
- `requests.get(..., stream=True)` -> 대용량 MP4 파일을 chunk 단위로 다운로드

### installed

- selenium
- seleniumwire
- webdriver-manager
