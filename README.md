# DAUM-CAFE-MP4-CRAWLER

## 학습

### Selenium

- WebDriverWait(browser, 10)
  - 브라우저에서 최대 10초까지 특정 조건을 기다리는 객체 생성
- id_input = wait.until(EC.element_to_be_clickable((By.NAME, "loginId")))
  - EC(Expected Conditions; 예상 조건)
  - HTML에서 <input name="loginId"> 태그를 찾음
  - 단순히 존재하는 것이 아니라 **클릭 가능한 상태**까지 기다림
    - 클릭 가능한 상태 = 요소가 보이고(visible) + 활성화되어 있음(enabled)
  - .clear()
    - 입력 필드에 기존에 입력되어 있던 텍스트를 삭제
  - .send_keys()
    - 새로운 값 입력

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