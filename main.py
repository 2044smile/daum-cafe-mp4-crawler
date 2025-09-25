import os
import time
from pathlib import Path
from dotenv import load_dotenv

from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


load_dotenv()

KAKAO_ID = os.getenv('KAKAO_ID')
KAKAO_PASSWORD = os.getenv('KAKAO_PASSWORD')
LOGIN_URL = os.getenv('LOGIN_URL')
TARGET_CAFE_URL = os.getenv('TARGET_CAFE_URL')

# 다운로드 폴더 생성
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

def extract_post_url_and_title(row):
    """게시글 행에서 URL과 제목 추출"""
    try:
        title_cell = None
        title_selectors = [".td_title", ".title", "td.title", "td:nth-child(3)", "td:nth-child(4)"]

        for selector in title_selectors:
            try:
                title_cell = row.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue

        if not title_cell:
            # 모든 td에서 링크가 있는 것 찾기
            tds = row.find_elements(By.TAG_NAME, "td")
            for td in tds:
                links = td.find_elements(By.TAG_NAME, "a")
                if links:
                    title_cell = td
                    break

        if title_cell:
            # 링크 찾기
            link_elements = title_cell.find_elements(By.TAG_NAME, "a")
            for link in link_elements:
                href = link.get_attribute('href')
                title = link.text.strip()

                if href and title and len(title) > 2:
                    # 게시글 URL 패턴 확인
                    valid_patterns = ['bbs_read', 'read', 'view', 'article']
                    is_valid_link = any(pattern in href.lower() for pattern in valid_patterns)

                    if is_valid_link:
                        return href, title

    except Exception as e:
        print(f"게시글 URL 추출 오류: {e}")

    return None, None

def analyze_post_streams(browser, post_url, post_title):
    """게시글의 네트워크 스트림 분석"""

    print(f"\n{'='*60}")
    print(f"🎬 게시글 스트림 분석: {post_title}...")
    print(f"{'='*60}")

    try:
        # 현재 네트워크 요청 기록 시작점 저장
        initial_request_count = len(browser.requests)
        print(f"📊 분석 시작 전 네트워크 요청: {initial_request_count}개")

        # 게시글로 이동 (iframe 유지된 상태)
        print(f"🔄 게시글로 이동 중...")
        browser.get(post_url)
        time.sleep(5)  # 페이지 로딩 및 비디오 로딩 대기

        # 비디오 요소 트리거 (자동 재생 또는 로딩 유도)
        print(f"🎥 비디오 요소 트리거 시도...")
        try:
            # 비디오 요소 찾기
            videos = browser.find_elements(By.TAG_NAME, "video")
            print(f"  📺 발견된 비디오 요소: {len(videos)}개")

            # iframe 내부의 비디오도 확인
            iframes = browser.find_elements(By.TAG_NAME, "iframe")
            print(f"  📺 발견된 iframe: {len(iframes)}개")

            # 비디오 재생 시도 (네트워크 요청 유도)
            for i, video in enumerate(videos):
                try:
                    browser.execute_script("arguments[0].play();", video)
                    print(f"    🎬 비디오 {i+1} 재생 시도")
                    time.sleep(2)
                except:
                    pass

        except Exception as e:
            print(f"  ⚠️ 비디오 트리거 오류: {e}")

        # 추가 로딩 대기
        print(f"⏳ 네트워크 스트림 로딩 대기...")
        time.sleep(8)

        # 🔍 kamp 요청이 완료될 때까지 추가 대기
        print(f"🔍 kamp 요청 완료 대기...")
        for retry in range(5):  # 최대 5번 재시도
            kamp_count = sum(1 for req in browser.requests[initial_request_count:]
                           if 'kamp.daum.net' in req.url.lower())
            if kamp_count > 0:
                print(f"  ✅ kamp 요청 {kamp_count}개 발견, 응답 완료 대기 중...")
                time.sleep(3)  # kamp 응답 완료 대기
                break
            else:
                print(f"  ⏳ kamp 요청 대기 중... ({retry+1}/5)")
                time.sleep(2)

        # 새로운 네트워크 요청 분석
        new_requests = browser.requests[initial_request_count:]
        print(f"📊 새로운 네트워크 요청: {len(new_requests)}개")

        # 🔍 네트워크 요청 캡처 확인 (디버깅)
        if len(new_requests) == 0:
            print("⚠️ 네트워크 요청이 캡처되지 않았습니다!")
            print("🔧 seleniumwire 프록시 상태 확인...")
            print(f"   프록시 설정: {browser.proxy if hasattr(browser, 'proxy') else '없음'}")
            print(f"   전체 요청 수: {len(browser.requests)}개")
        else:
            print("✅ 네트워크 요청 캡처 성공!")
            # 🔍 요청 도메인 미리보기 (처음 5개)
            print("📋 캡처된 요청 미리보기:")
            for i, req in enumerate(new_requests[:5]):
                try:
                    domain = req.url.split('/')[2] if '://' in req.url else req.url[:50]
                    print(f"   [{i+1}] {domain}")
                except:
                    print(f"   [{i+1}] {req.url[:50]}...")
            if len(new_requests) > 5:
                print(f"   ... 및 {len(new_requests)-5}개 더")

        # 스트림 파일 분석
        download_targets = analyze_stream_requests(new_requests)

        # 480p MP4 파일 다운로드
        if download_targets:
            print(f"\n📥 480p MP4 파일 다운로드 시작...")

            # 🥇 1순위: 간단한 requests 다운로드 (가장 확실!)
            print(f"\n🎯 간단한 requests 다운로드 시도...")

            # 간단한 다운로드 구현
            import requests
            success_count = 0

            for i, url in enumerate(download_targets, 1):
                try:
                    print(f"\n[{i}/{len(download_targets)}] 다운로드 중...")
                    print(f"🔗 URL: {url[:80]}...")

                    # 파일명 생성
                    filename = f"{post_title}_{i}_480p.mp4".replace('/', '_').replace('\\', '_').replace(':', '_')
                    filepath = DOWNLOAD_DIR / filename

                    print(f"📁 저장할 파일: {filename}")

                    # 간단한 스트리밍 다운로드
                    with requests.get(url, stream=True, timeout=30) as r:
                        r.raise_for_status()

                        total_size = int(r.headers.get('content-length', 0))
                        if total_size > 0:
                            print(f"📊 파일 크기: {total_size / (1024*1024):.2f} MB")

                        downloaded_size = 0

                        with open(filepath, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    downloaded_size += len(chunk)

                                    if total_size > 0:
                                        progress = (downloaded_size / total_size) * 100
                                        print(f"\r  📈 진행률: {progress:.1f}%", end='', flush=True)

                    if filepath.exists():
                        file_size = filepath.stat().st_size
                        print(f"\n✅ 다운로드 완료: {file_size / (1024*1024):.2f} MB")
                        success_count += 1

                    time.sleep(1)

                except Exception as e:
                    print(f"\n❌ 다운로드 실패: {e}")

            print(f"\n📊 다운로드 결과: {success_count}/{len(download_targets)}개 성공")

            # 다운로드 실패시에만 간단한 알림
            if success_count == 0:
                print(f"\n⚠️ 모든 다운로드가 실패했습니다. URL이나 네트워크 상태를 확인해주세요.")

        else:
            print(f"\n⚠️ 다운로드할 480p MP4 파일이 없습니다.")

    except Exception as e:
        print(f"❌ 게시글 스트림 분석 오류: {e}")
        import traceback
        traceback.print_exc()

def analyze_stream_requests(requests):
    """네트워크 요청에서 스트림 파일들 분석"""

    print(f"\n🔍 스트림 파일 분석 시작...")
    print(f"{'='*50}")

    # 파일 타입별 분류 및 다운로드 대상 초기화
    mp4_files = []
    hls_files = []  # .m3u8, .ts
    dash_files = []  # .mpd, .m4s
    other_video_files = []
    kamp_requests = []
    download_targets = []  # 🔧 다운로드 대상 초기화

    for i, request in enumerate(requests):
        try:
            url = request.url.lower()

            # kamp.daum.net 요청 (streams 데이터)
            if 'kamp.daum.net' in url:
                kamp_requests.append(request)
                print(f"  🎯 kamp 요청 발견: {request.url}")

            # MP4 파일
            elif '.mp4' in url:
                mp4_files.append(request)

                # 480p 확인
                if '480p' in url:
                    print(f"  ✅ 480p MP4 발견: {request.url}")
                else:
                    print(f"  📹 MP4 파일: {request.url}")

            # HLS 파일들
            elif '.m3u8' in url or '.ts' in url:
                hls_files.append(request)
                print(f"  📡 HLS 파일: {request.url}")

            # DASH 파일들
            elif '.mpd' in url or '.m4s' in url:
                dash_files.append(request)
                print(f"  📊 DASH 파일: {request.url}")

            # 기타 비디오 관련 파일들
            elif any(ext in url for ext in ['.webm', '.avi', '.mov', '.flv']):
                other_video_files.append(request)
                print(f"  🎥 기타 비디오: {request.url}")

        except Exception as e:
            print(f"  ❌ 요청 [{i}] 분석 오류: {e}")

    # 결과 요약
    print(f"\n📊 스트림 파일 분석 결과:")
    print(f"{'='*50}")
    print(f"  🎯 kamp 요청: {len(kamp_requests)}개")
    print(f"  ✅ MP4 파일: {len(mp4_files)}개")
    print(f"  📡 HLS 파일: {len(hls_files)}개")
    print(f"  📊 DASH 파일: {len(dash_files)}개")
    print(f"  🎥 기타 비디오: {len(other_video_files)}개")

    # kamp 요청에서 streams 데이터 추출 (개선된 파싱)
    if kamp_requests:
        print(f"\n🔍 kamp 요청에서 streams 데이터 추출...")
        for i, request in enumerate(kamp_requests):
            try:
                print(f"  🔍 kamp [{i+1}] 요청 상태 확인...")
                print(f"     URL: {request.url}")
                print(f"     응답 있음: {request.response is not None}")
                if request.response:
                    print(f"     상태 코드: {request.response.status_code}")
                    print(f"     응답 바디 있음: {request.response.body is not None}")
                    print(f"     응답 헤더: {dict(request.response.headers)}")

                if request.response and request.response.body:
                    # 🔧 gzip 압축 해제 처리
                    raw_body = request.response.body

                    try:
                        # gzip 압축 확인 및 해제
                        if request.response.headers.get('content-encoding') == 'gzip':
                            import gzip
                            body = gzip.decompress(raw_body).decode('utf-8', errors='ignore')
                            print(f"  ✅ gzip 압축 해제 성공!")
                        else:
                            body = raw_body.decode('utf-8', errors='ignore')
                    except Exception as decompress_error:
                        print(f"  ⚠️ 압축 해제 실패: {decompress_error}")
                        # 원시 바이트로 시도
                        try:
                            body = raw_body.decode('utf-8', errors='ignore')
                        except:
                            body = str(raw_body)

                    # 🔍 kamp 응답 전체 내용 디버깅
                    print(f"  📋 kamp [{i+1}] 응답 크기: {len(body)} bytes")
                    print(f"  📄 응답 내용 (처음 500자): {body[:500]}...")
                    print(f"  🔍 'streams' 포함 여부: {'streams' in body}")
                    print(f"  🔍 'stream' 포함 여부: {'stream' in body}")
                    print(f"  🔍 'mp4' 포함 여부: {'mp4' in body}")
                    print(f"  🔍 '480' 포함 여부: {'480' in body}")

                    if 'streams' in body:
                        print(f"  ✅ kamp 요청 [{i+1}]에서 streams 데이터 발견!")

                        # JSON 파싱 시도
                        try:
                            import json
                            data = json.loads(body)

                            if 'streams' in data:
                                streams = data['streams']
                                print(f"    📊 streams 데이터 타입: {type(streams)}")
                                print(f"    📋 streams 내용: {streams}")

                                # streams가 리스트인 경우 (실제 구조에 맞춤)
                                if isinstance(streams, list):
                                    print(f"    🎬 streams 배열에서 480p MP4 검색 (총 {len(streams)}개):")
                                    for j, stream in enumerate(streams):
                                        if isinstance(stream, dict):
                                            name = stream.get('name', '')
                                            protocol = stream.get('protocol', '')
                                            url = stream.get('url', '')
                                            status = stream.get('status', '')

                                            print(f"      [{j+1}] name='{name}', protocol='{protocol}', status='{status}'")
                                            print(f"           URL: {url[:80]}..." if url else "           URL: 없음")

                                            # 🎯 정확한 조건: name="480p" AND protocol="mp4"
                                            if name == '480p' and protocol == 'mp4' and url:
                                                print(f"      🎉 정확한 480p MP4 스트림 발견!")
                                                download_targets.append(url)
                                            # 🎯 백업 조건: 480p가 이름에 포함되고 URL이 MP4
                                            elif '480' in name.lower() and url and '.mp4' in url.lower():
                                                print(f"      ✅ 480p MP4 패턴 발견!")
                                                download_targets.append(url)
                                            # 🎯 추가 조건: URL에서 직접 480P 패턴 확인
                                            elif url and ('480p' in url.lower() or '480P' in url) and '.mp4' in url.lower():
                                                print(f"      ✅ URL에서 480P MP4 패턴 발견!")
                                                download_targets.append(url)

                                # streams가 딕셔너리인 경우 (기존 방식)
                                elif isinstance(streams, dict):
                                    print(f"    🎬 streams 딕셔너리에서 480p 검색:")
                                    for quality, stream_data in streams.items():
                                        print(f"      화질: '{quality}'")

                                        if '480' in quality.lower():
                                            if isinstance(stream_data, str):
                                                print(f"      ✅ 480p URL: {stream_data}")
                                                download_targets.append(stream_data)
                                            elif isinstance(stream_data, dict) and 'url' in stream_data:
                                                url = stream_data['url']
                                                print(f"      ✅ 480p URL: {url}")
                                                download_targets.append(url)

                        except json.JSONDecodeError:
                            print(f"    ⚠️ JSON 파싱 실패, 원시 데이터에서 streams 검색")

                            # 원시 텍스트에서 480p URL 패턴 찾기
                            import re
                            mp4_pattern = r'https?://[^\s"\']+480[pP][^\s"\']*\.mp4[^\s"\']*'
                            matches = re.findall(mp4_pattern, body)

                            if matches:
                                print(f"    ✅ 원시 데이터에서 {len(matches)}개 480p MP4 URL 발견")
                                for match in matches:
                                    print(f"      🔗 {match}")
                                    download_targets.append(match)
                    else:
                        print(f"  ⚠️ kamp 요청 [{i+1}]에 streams 데이터 없음")

            except Exception as e:
                print(f"  ❌ kamp 요청 [{i+1}] 분석 오류: {e}")

    # 🔍 모든 요청에서 Daum 비디오 URL 검색 (핵심 수정!)
    print(f"\n🔍 전체 요청에서 Daum 비디오 URL 검색...")
    for request in requests:
        try:
            url = request.url
            url_lower = url.lower()

            # Daum 비디오 도메인 + MP4 + 480P 패턴
            daum_domains = ['play.daum.net', 'kdnv-skb-orisa-edge.play.daum.net', 'kamp.daum.net']

            if any(domain in url_lower for domain in daum_domains) and '.mp4' in url_lower:
                # 480P 확인 (대소문자 구분 없이)
                if '480p' in url_lower or '480P' in url:
                    if url not in download_targets:
                        download_targets.append(url)
                        print(f"  🎉 Daum 480P MP4 발견: {url}")

            # orisa-token이 포함된 MP4 URL (추가 검색)
            elif 'orisa-token' in url_lower and '.mp4' in url_lower:
                if url not in download_targets:
                    download_targets.append(url)
                    print(f"  🎯 orisa-token MP4 발견: {url}")

        except Exception as e:
            continue

    # 일반 MP4 요청에서도 480p 찾기 (기존 로직 유지)
    for request in mp4_files:
        url = request.url
        if '480p' in url.lower() and url not in download_targets:
            download_targets.append(url)
            print(f"  ✅ 일반 요청에서 480p 발견: {url}")

    # 최종 결과 표시
    print(f"\n🎯 최종 다운로드 대상:")
    print(f"{'='*50}")

    if download_targets:
        for i, url in enumerate(download_targets, 1):
            print(f"  [{i}] {url}")
    else:
        print(f"  ⚠️ 480p MP4 파일을 찾을 수 없습니다.")

        # 다른 화질 MP4도 표시
        if mp4_files:
            print(f"\n📋 발견된 다른 화질 MP4:")
            for request in mp4_files:
                url = request.url
                print(f"    📹 {url}")

    return download_targets

if __name__ == "__main__":
    customService = Service(ChromeDriverManager().install())
    customOption = Options()

    # 🔧 Chrome 옵션 개선 (HTTP protocol error 방지)
    customOption.add_argument('--disable-web-security')
    customOption.add_argument('--allow-running-insecure-content')
    customOption.add_argument('--disable-features=VizDisplayCompositor')
    customOption.add_argument('--no-sandbox')  # Linux에서 필요할 수 있음
    customOption.add_argument('--disable-dev-shm-usage')  # 메모리 문제 방지

    # 🔧 seleniumwire 설정 (네트워크 요청 캡처를 위해 필수!)
    seleniumwire_options = {
        'addr': '127.0.0.1',  # 프록시 주소
        'port': 0,  # 자동 포트 할당
        'auto_config': True,  # 자동 설정
        'suppress_connection_errors': True,  # 🔧 연결 오류 억제 (HTTP protocol error 방지)
        'verify_ssl': False,  # SSL 검증 비활성화
        'connection_timeout': 30,  # 연결 타임아웃
        'read_timeout': 30,  # 읽기 타임아웃
    }

    print("🔧 seleniumwire 프록시 설정 중...")

    # 로그인 (seleniumwire_options 추가!)
    browser = webdriver.Chrome(
        service=customService,
        options=customOption,
        seleniumwire_options=seleniumwire_options
    )

    print(f"✅ seleniumwire 프록시 활성화: {browser.proxy}")
    print("📡 이제 모든 네트워크 요청이 캡처됩니다!")
    wait = WebDriverWait(browser, 10)

    browser.get(LOGIN_URL)
    time.sleep(3)

    # ID 입력 필드 대기 및 입력
    try:
        id_input = wait.until(EC.element_to_be_clickable((By.NAME, "loginId")))
        id_input.clear()
        time.sleep(0.5)

        id_input.send_keys(KAKAO_ID)
        print(f"ID 입력 완료: {KAKAO_ID}")
    except Exception as e:
        print(f"ID 입력 실패: {e}")
    
    # 비밀번호 입력 필드 대기 및 입력
    try:
        pw_input = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        pw_input.clear()
        time.sleep(0.5)
        pw_input.send_keys(KAKAO_PASSWORD)
        print("비밀번호 입력 완료")
    except Exception as e:
        print(f"비밀번호 입력 실패: {e}")
    
    try:
        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        browser.execute_script("arguments[0].click();", login_btn)
        print("로그인 버튼 클릭 완료")
    except Exception as e:
        print(f"로그인 버튼 클릭 실패 {e}")
    
    # 로그인 처리 대기
    time.sleep(5)

    # 현재 URL 확인
    print(f"현재 URL: {browser.current_url}")

    # 카페로 이동
    time.sleep(5)
    browser.get(TARGET_CAFE_URL)
    time.sleep(5)

    # 특정 게시판으로 이동
    board_url = f"{TARGET_CAFE_URL}/ThHa"
    browser.get(board_url)
    print(f"현재 URL: {browser.current_url}")
    time.sleep(5)

    # 게시글 목록 확인
    print("=" * 60)
    print("🔍 게시판 분석 시작")
    print("=" * 60)

    # 1. 페이지 로딩 완료 대기
    print("⏳ 페이지 로딩 대기 중...")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    time.sleep(3)

    # 1-1. iframe 확인 및 전환
    print("🔍 iframe 확인 중...")

    # iframe 찾기
    iframes = browser.find_elements(By.TAG_NAME, "iframe")
    print(f"📊 발견된 iframe: {len(iframes)}개")

    for i, iframe in enumerate(iframes):
        try:
            iframe_src = iframe.get_attribute("src") or ""
            iframe_id = iframe.get_attribute("id") or ""
            iframe_name = iframe.get_attribute("name") or ""
            print(f"  [{i+1}] iframe - id: '{iframe_id}', name: '{iframe_name}', src: {iframe_src[:100]}...")
        except Exception as e:
            print(f"  [{i+1}] iframe 정보 확인 오류: {e}")

    # 메인 게시판 iframe으로 전환 시도
    board_iframe_found = False

    # 실제로 작동하는 iframe만 (로그 가독성 향상)
    iframe_candidates = [
        "down"
    ]

    for iframe_name in iframe_candidates:
        try:
            print(f"🔄 iframe '{iframe_name}' 전환 시도...")
            browser.switch_to.frame(iframe_name)

            # iframe 전환 후 잠시 대기 (tests.py 방식)
            time.sleep(2)

            # iframe 내부에서 article-list 확인 (tests.py 방식)
            try:
                browser.find_element(By.ID, "article-list")
                print(f"✅ iframe '{iframe_name}' 전환 성공! (article-list 발견)")

                # 바로 여기서 게시글 리스트 확인
                print("🔍 게시글 리스트 즉시 확인 중...")

                # 게시글 행 찾기 (tests.py 방식)
                row_selectors = [
                    "#article-list tbody tr:not(.state_info)",  # 공지사항 제외
                    "#article-list tbody tr",  # 모든 행
                    "#article-list tr:not(.state_info)",  # tbody 없이
                    "#article-list tr",  # 모든 행 (tbody 없이)
                ]

                post_rows = []
                for selector in row_selectors:
                    try:
                        rows = browser.find_elements(By.CSS_SELECTOR, selector)
                        if rows:
                            post_rows = rows
                            print(f"  ✅ 게시글 행 {len(post_rows)}개 발견 (선택자: {selector})")
                            break
                    except:
                        continue

                if post_rows:
                    print(f"\n🎯 SjqQ 게시판에서 모든 페이지의 모든 게시글 처리 시작...")

                    # 페이지네이션 처리 (무제한, 마지막 페이지까지)
                    page_num = 1
                    while True:  # 마지막 페이지까지 무제한 루프
                        print(f"\n{'='*60}")
                        print(f"📄 {page_num}페이지 처리 중...")
                        print(f"{'='*60}")

                        # 2페이지부터는 페이지 이동
                        if page_num > 1:
                            try:
                                print(f"🔄 {page_num}페이지로 이동 중...")

                                # 페이지 번호 링크 찾기 (여러 방법 시도)
                                page_selectors = [
                                    "a.link_num span.num_item",
                                    "a[href*='javascript:'] span",
                                    "a[href*='page'] span",
                                ]

                                page_found = False
                                for selector in page_selectors:
                                    try:
                                        page_elements = browser.find_elements(By.CSS_SELECTOR, selector)
                                        for element in page_elements:
                                            if element.text.strip() == str(page_num):
                                                page_button = element.find_element(By.XPATH, "..")
                                                page_button.click()
                                                print(f"  ✅ {page_num}페이지 클릭 성공")
                                                time.sleep(3)  # 페이지 로딩 대기
                                                page_found = True
                                                break
                                        if page_found:
                                            break
                                    except:
                                        continue

                                if not page_found:
                                    print(f"  ⚠️ {page_num}페이지 버튼을 찾을 수 없음. 더 이상 페이지가 없을 가능성")
                                    break

                            except Exception as e:
                                print(f"  ❌ {page_num}페이지 이동 실패: {e}")
                                break

                        # 현재 페이지의 게시글 목록 다시 가져오기
                        current_post_rows = []
                        for selector in row_selectors:
                            try:
                                rows = browser.find_elements(By.CSS_SELECTOR, selector)
                                if rows:
                                    current_post_rows = rows
                                    print(f"  ✅ {page_num}페이지에서 게시글 {len(current_post_rows)}개 발견")
                                    break
                            except:
                                continue

                        if not current_post_rows:
                            print(f"  ❌ {page_num}페이지에서 게시글을 찾을 수 없음")
                            continue

                        # 먼저 모든 게시글의 URL과 제목을 수집 (stale element 문제 방지)
                        print(f"  🔍 {page_num}페이지의 모든 게시글 URL 수집 중...")
                        post_data_list = []

                        for i, row in enumerate(current_post_rows):
                            try:
                                post_url, post_title = extract_post_url_and_title(row)
                                if post_url and post_title:
                                    post_data_list.append((post_url, post_title))
                                    print(f"    ✅ [{page_num}-{i+1}] {post_title[:50]}...")
                                else:
                                    print(f"    ❌ [{page_num}-{i+1}] URL 추출 실패")
                            except Exception as e:
                                print(f"    ❌ [{page_num}-{i+1}] URL 수집 오류: {e}")

                        print(f"  📊 {page_num}페이지에서 {len(post_data_list)}개 게시글 URL 수집 완료")

                        # 수집된 URL들을 하나씩 처리
                        for i, (post_url, post_title) in enumerate(post_data_list, 1):
                            try:
                                print(f"\n  🎬 [{page_num}-{i}] 게시글 처리 중...")
                                print(f"    📋 제목: {post_title[:50]}...")
                                print(f"    🔗 URL: {post_url}")

                                # 게시글 분석 및 다운로드
                                analyze_post_streams(browser, post_url, f"[{page_num}-{i}]{post_title}")

                                # 게시판으로 다시 돌아가기
                                print(f"    🔄 게시판으로 돌아가는 중...")
                                browser.back()
                                time.sleep(2)

                                # iframe 다시 전환 (게시글에서 돌아온 후)
                                try:
                                    browser.switch_to.frame("down")
                                    time.sleep(1)
                                except:
                                    print(f"    ⚠️ iframe 재전환 실패")

                            except Exception as e:
                                print(f"    ❌ 게시글 [{page_num}-{i}] 처리 오류: {e}")
                                # 오류 발생시 게시판으로 돌아가기
                                try:
                                    browser.back()
                                    time.sleep(2)
                                    browser.switch_to.frame("down")
                                except:
                                    pass

                        print(f"\n✅ {page_num}페이지 처리 완료")

                        # 다음 페이지 존재 여부 확인
                        next_page_num = page_num + 1
                        next_page_exists = False

                        try:
                            # 다음 페이지 번호가 있는지 확인
                            page_elements = browser.find_elements(By.CSS_SELECTOR, "a.link_num span.num_item")
                            for element in page_elements:
                                if element.text.strip() == str(next_page_num):
                                    next_page_exists = True
                                    break

                            # 다음 버튼도 확인
                            if not next_page_exists:
                                next_button_selectors = [
                                    "a.link_next",  # 다음 버튼 클래스
                                    "a[href*='javascript:'][title*='다음']",  # 제목에 다음이 포함
                                    "a[href*='javascript:']"  # 모든 자바스크립트 링크 중에서
                                ]

                                for selector in next_button_selectors:
                                    try:
                                        buttons = browser.find_elements(By.CSS_SELECTOR, selector)
                                        for button in buttons:
                                            button_text = button.text.strip()
                                            if ('다음' in button_text or '>' in button_text) and button.is_enabled():
                                                next_page_exists = True
                                                break
                                        if next_page_exists:
                                            break
                                    except:
                                        continue

                        except Exception as e:
                            print(f"  ⚠️ 다음 페이지 확인 중 오류: {e}")

                        if not next_page_exists:
                            print(f"\n🏁 마지막 페이지({page_num}페이지)에 도달했습니다.")
                            break

                        page_num += 1  # 다음 페이지로

                    print(f"\n🎉 SjqQ 게시판 모든 페이지({page_num}페이지)의 모든 게시글 처리 완료!")

                else:
                    print("  ❌ 게시글 행을 찾을 수 없음")

                board_iframe_found = True
                break
            except:
                print(f"  ⚠️ iframe '{iframe_name}' - article-list 없음")
                browser.switch_to.default_content()
                continue

        except Exception as e:
            print(f"  ❌ iframe '{iframe_name}' 전환 실패: {e}")
            # 메인 프레임으로 돌아가기
            try:
                browser.switch_to.default_content()
            except:
                pass

    # 이름으로 안되면 인덱스로 시도
    if not board_iframe_found and len(iframes) > 0:
        for i, iframe in enumerate(iframes):
            try:
                print(f"🔄 iframe 인덱스 [{i}] 전환 시도...")
                browser.switch_to.default_content()  # 메인으로 돌아가기
                browser.switch_to.frame(i)

                # iframe 전환 후 대기 (tests.py 방식)
                time.sleep(2)

                # article-list 확인 (tests.py 방식)
                try:
                    browser.find_element(By.ID, "article-list")
                    print(f"✅ iframe 인덱스 [{i}] 전환 성공! (article-list 발견)")
                    board_iframe_found = True
                    break
                except:
                    print(f"  ⚠️ iframe 인덱스 [{i}] - article-list 없음")

            except Exception as e:
                print(f"  ❌ iframe 인덱스 [{i}] 전환 실패: {e}")
                try:
                    browser.switch_to.default_content()
                except:
                    pass

    if not board_iframe_found:
        print("⚠️ 적절한 iframe을 찾지 못했습니다. 메인 프레임에서 진행합니다.")
        browser.switch_to.default_content()

    print("✅ iframe 처리 완료")
    time.sleep(2)