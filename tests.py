import os
import time
import requests
import re
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

load_dotenv()

KAKAO_ID = os.getenv('KAKAO_ID')
KAKAO_PASSWORD = os.getenv('KAKAO_PASSWORD')
LOGIN_URL = os.getenv('LOGIN_URL')
TARGET_CAFE_URL = os.getenv('TARGET_CAFE_URL')

# 다운로드 폴더 생성
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

if not all([KAKAO_ID, KAKAO_PASSWORD, TARGET_CAFE_URL]):
    raise ValueError("필수 환경변수가 설정되지 않았습니다.")

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def switch_to_cafe_iframe():
    """카페 iframe으로 전환"""
    try:
        # 잠시 대기
        time.sleep(3)
        
        # iframe 찾기
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"발견된 iframe 개수: {len(iframes)}")
        
        for i, iframe in enumerate(iframes):
            try:
                iframe_src = iframe.get_attribute('src')
                iframe_name = iframe.get_attribute('name')
                iframe_id = iframe.get_attribute('id')
                
                print(f"iframe {i+1}: src={iframe_src}, name={iframe_name}, id={iframe_id}")
                
                # 카페 관련 iframe인지 확인 (보통 cafe_main이나 비슷한 이름)
                if (iframe_name and 'cafe' in iframe_name.lower()) or \
                   (iframe_id and 'cafe' in iframe_id.lower()) or \
                   (iframe_src and 'cafe' in iframe_src):
                    
                    print(f"카페 iframe으로 전환: {iframe_name or iframe_id}")
                    driver.switch_to.frame(iframe)
                    
                    # iframe 전환 후 잠시 대기
                    time.sleep(2)
                    
                    # iframe 내부에서 article-list 확인
                    try:
                        article_table = driver.find_element(By.ID, "article-list")
                        print("✅ iframe에서 article-list 발견!")
                        return True
                    except:
                        print("이 iframe에는 article-list가 없음")
                        driver.switch_to.default_content()
                        continue
                        
            except Exception as e:
                print(f"iframe {i+1} 처리 실패: {e}")
                driver.switch_to.default_content()
                continue
        
        # 특정 iframe 이름으로 직접 시도
        try:
            driver.switch_to.frame("cafe_main")
            print("✅ cafe_main iframe으로 전환")
            return True
        except:
            print("cafe_main iframe 없음")
        
        print("❌ 적절한 iframe을 찾지 못함")
        return False
        
    except Exception as e:
        print(f"iframe 전환 실패: {e}")
        return False

def download_mp4(url, filename):
    """MP4 파일 다운로드"""
    try:
        print(f"다운로드 시작: {filename}")
        
        session = requests.Session()
        # Selenium 쿠키를 requests에 추가
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': driver.current_url
        }
        
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        filepath = DOWNLOAD_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 다운로드 완료: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ 다운로드 실패: {filename} - {e}")
        return False

def extract_mp4_urls():
    """현재 페이지에서 MP4 URL들 추출"""
    mp4_urls = []
    
    # 방법 1: video 태그
    video_elements = driver.find_elements(By.TAG_NAME, "video")
    for video in video_elements:
        src = video.get_attribute("src")
        if src and src.endswith('.mp4'):
            mp4_urls.append(src)
    
    # 방법 2: source 태그
    source_elements = driver.find_elements(By.TAG_NAME, "source")
    for source in source_elements:
        src = source.get_attribute("src")
        if src and src.endswith('.mp4'):
            mp4_urls.append(src)
    
    # 방법 3: a 태그 mp4 링크
    link_elements = driver.find_elements(By.TAG_NAME, "a")
    for link in link_elements:
        href = link.get_attribute("href")
        if href and href.endswith('.mp4'):
            mp4_urls.append(href)
    
    # 방법 4: 페이지 소스에서 정규식
    page_source = driver.page_source
    mp4_pattern = r'https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*'
    regex_matches = re.findall(mp4_pattern, page_source, re.IGNORECASE)
    mp4_urls.extend(regex_matches)
    
    # 중복 제거
    mp4_urls = list(set(mp4_urls))
    return mp4_urls

def get_post_links_from_current_page():
    """현재 페이지에서 게시글 링크들 수집"""
    post_links = []
    
    try:
        # iframe으로 전환
        if not switch_to_cafe_iframe():
            print("iframe 전환 실패")
            return []
        
        # 테이블 로딩 확인
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.ID, "article-list")))
        
        print("게시글 테이블 발견됨")
        
        # 모든 게시글 행 찾기 (공지사항 제외)
        post_rows = driver.find_elements(By.CSS_SELECTOR, "#article-list tr:not(.state_info)")
        print(f"일반 게시글 행: {len(post_rows)}개")
        
        if not post_rows:
            # 공지사항 포함해서 다시 시도
            post_rows = driver.find_elements(By.CSS_SELECTOR, "#article-list tr")
            print(f"전체 게시글 행 (공지 포함): {len(post_rows)}개")
        
        for i, row in enumerate(post_rows):
            try:
                # 각 행에서 제목 칸 찾기
                title_cell = row.find_element(By.CLASS_NAME, "td_title")
                
                # 제목 칸 안의 링크 찾기
                link_elements = title_cell.find_elements(By.TAG_NAME, "a")
                
                for link in link_elements:
                    href = link.get_attribute('href')
                    title = link.text.strip()
                    
                    # 유효한 게시글 링크인지 확인
                    if href and 'bbs_read' in href and title and len(title) > 1:
                        post_links.append({
                            'url': href,
                            'title': title
                        })
                        print(f"  {len(post_links)}. {title}")
                        break  # 첫 번째 유효한 링크만 가져오기
                        
            except Exception as e:
                print(f"행 {i} 처리 중 오류: {e}")
                continue
        
        print(f"총 {len(post_links)}개 게시글 링크 수집")
        
        # iframe에서 나가기
        driver.switch_to.default_content()
        return post_links
        
    except Exception as e:
        print(f"게시글 수집 실패: {e}")
        
        # iframe에서 나가기
        driver.switch_to.default_content()
        
        # 디버깅: 다른 방법으로 링크 찾기
        try:
            print("대안 방법으로 링크 찾기...")
            
            # iframe 다시 시도
            if switch_to_cafe_iframe():
                # 모든 링크 중에서 bbs_read 포함된 것들 찾기
                all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='bbs_read']")
                print(f"bbs_read 포함 링크: {len(all_links)}개")
                
                for link in all_links:
                    href = link.get_attribute('href')
                    title = link.text.strip()
                    
                    if title and len(title) > 1:
                        post_links.append({
                            'url': href,
                            'title': title
                        })
                
                print(f"대안 방법으로 {len(post_links)}개 수집")
                driver.switch_to.default_content()
                return post_links
            
        except Exception as e2:
            print(f"대안 방법도 실패: {e2}")
            driver.switch_to.default_content()
            return []

def click_next_page():
    """다음 페이지 클릭"""
    try:
        # iframe으로 전환
        if not switch_to_cafe_iframe():
            return False
        
        # 페이지네이션 영역에서 다음 버튼 찾기
        next_selectors = [
            ".paging_g .btn_next:not([disabled])",  # 활성화된 다음 버튼
            ".paging_g .btn_item.btn_next:not([disabled])",
            ".list_paging li:last-child a",  # 마지막 페이지 번호
        ]
        
        for selector in next_selectors:
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, selector)
                if next_button.is_enabled() and next_button.is_displayed():
                    driver.execute_script("arguments[0].click();", next_button)
                    print("다음 페이지 클릭 성공")
                    driver.switch_to.default_content()
                    time.sleep(3)
                    return True
            except:
                continue
        
        # 숫자 페이지 버튼 클릭 시도
        try:
            page_numbers = driver.find_elements(By.CSS_SELECTOR, ".list_paging li:not(.on) a")
            if page_numbers:
                next_page = page_numbers[0]  # 첫 번째 비활성 페이지
                driver.execute_script("arguments[0].click();", next_page)
                print("다음 페이지 번호 클릭")
                driver.switch_to.default_content()
                time.sleep(3)
                return True
        except:
            pass
        
        print("다음 페이지 버튼을 찾을 수 없음")
        driver.switch_to.default_content()
        return False
        
    except Exception as e:
        print(f"페이지 이동 오류: {e}")
        driver.switch_to.default_content()
        return False

try:
    wait = WebDriverWait(driver, 10)
    
    # 로그인
    print("카카오 로그인 중...")
    driver.get(LOGIN_URL)
    
    id_input = wait.until(EC.presence_of_element_located((By.NAME, "loginId")))
    id_input.clear()
    id_input.send_keys(KAKAO_ID)
    
    pw_input = driver.find_element(By.NAME, "password")
    pw_input.clear()
    pw_input.send_keys(KAKAO_PASSWORD)
    
    login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_btn.click()
    
    time.sleep(3)
    input("인증 완료 후 Enter를 누르세요.")
    
    # 카페 게시판으로 이동
    driver.get(TARGET_CAFE_URL)
    time.sleep(3)
    driver.get(f"{driver.current_url}/SjqQ")
    time.sleep(5)  # iframe 로딩 대기
    
    print(f"현재 게시판: {driver.current_url}")
    
    total_downloads = 0
    page_count = 1
    max_pages = 5
    
    while page_count <= max_pages:
        print(f"\n{'='*50}")
        print(f"📄 {page_count}페이지 처리 중...")
        print(f"{'='*50}")
        
        # 현재 페이지의 게시글 링크 수집
        post_links = get_post_links_from_current_page()
        
        if not post_links:
            print("❌ 게시글을 찾을 수 없습니다.")
            break
        
        print(f"발견된 게시글: {len(post_links)}개")
        
        # 각 게시글 처리
        for i, post in enumerate(post_links[:10], 1):
            print(f"\n[게시글 {i}/{min(10, len(post_links))}] 처리: {post['title']}")
            
            try:
                # 새 탭에서 게시글 열기
                driver.execute_script(f"window.open('{post['url']}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)
                
                # MP4 URL 추출
                mp4_urls = extract_mp4_urls()
                
                if mp4_urls:
                    print(f"MP4 파일 {len(mp4_urls)}개 발견!")
                    for j, mp4_url in enumerate(mp4_urls):
                        filename = f"page_{page_count}_post_{i}_video_{j+1}.mp4"
                        if download_mp4(mp4_url, filename):
                            total_downloads += 1
                else:
                    print("MP4 파일 없음")
                
                # 탭 닫기
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
                time.sleep(1)
                
            except Exception as e:
                print(f"게시글 처리 중 오류: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
        
        # 다음 페이지로 이동
        page_count += 1
        if page_count <= max_pages:
            print(f"\n다음 페이지({page_count})로 이동 중...")
            if not click_next_page():
                print("더 이상 페이지가 없습니다.")
                break
    
    print(f"\n🎉 크롤링 완료!")
    print(f"📊 총 {page_count-1}페이지 처리")
    print(f"📁 총 {total_downloads}개 파일 다운로드")
    print(f"📂 다운로드 폴더: {DOWNLOAD_DIR.absolute()}")

except Exception as e:
    print(f"오류 발생: {e}")
    import traceback
    traceback.print_exc()

finally:
    input("작업 완료. Enter를 누르면 브라우저가 종료됩니다...")
    # driver.quit()