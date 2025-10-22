#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 자동 로그인 GUI 프로그램
도메인을 입력하면 자동으로 /wp-admin에 접속하고 로그인을 수행합니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import os
import glob
from urllib.parse import urlparse, urljoin

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class WordPressAutoLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("WordPress 자동 로그인 프로그램")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 변수 초기화
        self.driver = None
        self.is_logged_in = False
        self.txt_files_dir = r"C:\Users\4-002\Desktop\강동혁\python\테스트"
        
        # GUI 구성 요소 생성
        self.create_widgets()
        
        # Selenium 사용 가능 여부 확인
        if not SELENIUM_AVAILABLE:
            self.log_message("오류: Selenium이 설치되지 않았습니다. pip install selenium webdriver-manager를 실행해주세요.")
            self.login_button.config(state='disabled')
    
    def create_widgets(self):
        """GUI 위젯들을 생성합니다."""
        
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="WordPress 자동 로그인", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 도메인 입력
        ttk.Label(main_frame, text="도메인 주소:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.domain_var = tk.StringVar(value="https://")
        self.domain_entry = ttk.Entry(main_frame, textvariable=self.domain_var, width=40)
        self.domain_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 아이디 입력
        ttk.Label(main_frame, text="아이디:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(main_frame, textvariable=self.username_var, width=40)
        self.username_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 비밀번호 입력
        ttk.Label(main_frame, text="비밀번호:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, 
                                       width=40, show="*")
        self.password_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # 로그인 버튼
        self.login_button = ttk.Button(button_frame, text="로그인", 
                                      command=self.start_login_thread)
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        # 로그아웃 버튼
        self.logout_button = ttk.Button(button_frame, text="로그아웃", 
                                       command=self.logout, state='disabled')
        self.logout_button.pack(side=tk.LEFT, padx=5)
        
        # 브라우저 열기 버튼
        self.open_browser_button = ttk.Button(button_frame, text="브라우저에서 열기", 
                                             command=self.open_in_browser, state='disabled')
        self.open_browser_button.pack(side=tk.LEFT, padx=5)
        
        # 상태 표시
        self.status_var = tk.StringVar(value="준비됨")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 로그 영역
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="5")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=70, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Enter 키 바인딩
        self.root.bind('<Return>', lambda e: self.start_login_thread())
        
        # 초기 메시지
        self.log_message("WordPress 자동 로그인 프로그램이 시작되었습니다.")
        self.log_message("도메인 주소를 입력하고 로그인 정보를 입력한 후 '로그인' 버튼을 클릭하세요.")
        self.log_message(f"텍스트 파일 경로: {self.txt_files_dir}")
    
    def get_txt_files(self):
        """텍스트 파일 목록을 가져옵니다."""
        if not os.path.exists(self.txt_files_dir):
            self.log_message(f"❌ 텍스트 파일 폴더가 존재하지 않습니다: {self.txt_files_dir}")
            return []
        
        txt_files = glob.glob(os.path.join(self.txt_files_dir, "*.txt"))
        return txt_files
    
    def read_txt_file(self, file_path):
        """텍스트 파일을 읽어서 내용을 반환합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            return content
        except Exception as e:
            self.log_message(f"❌ 파일 읽기 실패 ({file_path}): {str(e)}")
            return None
    
    def get_post_data(self):
        """첫 번째 txt 파일에서 제목과 내용을 가져옵니다."""
        txt_files = self.get_txt_files()
        if not txt_files:
            self.log_message("❌ 텍스트 파일을 찾을 수 없습니다.")
            return None, None
        
        # 첫 번째 파일 사용
        file_path = txt_files[0]
        filename = os.path.basename(file_path)
        
        # 파일 내용 읽기
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) < 3:
                self.log_message("❌ 파일에 충분한 줄이 없습니다. (최소 3줄 필요)")
                return None, None
            
            # 첫 번째 줄이 제목
            title = lines[0].strip()
            
            # 세 번째 줄부터가 본문 (줄 번호는 0부터 시작하므로 인덱스 2부터)
            content_lines = lines[2:]  # 세 번째 줄부터 끝까지
            content = ''.join(content_lines).strip()
            
            self.log_message(f"📝 파일에서 읽은 제목: {title}")
            self.log_message(f"📝 파일에서 읽은 본문 길이: {len(content)}자")
            self.log_message(f"📝 사용된 파일: {filename}")
            
            return title, content
            
        except Exception as e:
            self.log_message(f"❌ 파일 읽기 실패 ({filename}): {str(e)}")
            return None, None
    
    def log_message(self, message):
        """로그 메시지를 추가합니다."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def validate_inputs(self):
        """입력값을 검증합니다."""
        domain = self.domain_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not domain:
            messagebox.showerror("오류", "도메인 주소를 입력해주세요.")
            return False
        
        if not username:
            messagebox.showerror("오류", "아이디를 입력해주세요.")
            return False
        
        if not password:
            messagebox.showerror("오류", "비밀번호를 입력해주세요.")
            return False
        
        # URL 형식 검증
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain
            self.domain_var.set(domain)
        
        try:
            parsed = urlparse(domain)
            if not parsed.netloc:
                messagebox.showerror("오류", "올바른 도메인 주소를 입력해주세요.")
                return False
        except Exception:
            messagebox.showerror("오류", "올바른 도메인 주소를 입력해주세요.")
            return False
        
        return True
    
    def start_login_thread(self):
        """로그인을 별도 스레드에서 시작합니다."""
        if not self.validate_inputs():
            return
        
        # 버튼 상태 변경
        self.login_button.config(state='disabled')
        self.status_var.set("로그인 진행 중...")
        
        # 별도 스레드에서 로그인 실행
        thread = threading.Thread(target=self.perform_login)
        thread.daemon = True
        thread.start()
    
    def perform_login(self):
        """실제 로그인을 수행합니다."""
        try:
            domain = self.domain_var.get().strip()
            username = self.username_var.get().strip()
            password = self.password_var.get().strip()
            
            # wp-admin URL 생성
            admin_url = urljoin(domain.rstrip('/') + '/', 'wp-admin/')
            
            self.log_message(f"WordPress 관리자 페이지에 접속합니다: {admin_url}")
            
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # WebDriver 초기화
            self.log_message("브라우저를 시작하고 있습니다...")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 페이지 로드
            self.driver.get(admin_url)
            self.log_message("WordPress 로그인 페이지를 로드했습니다.")
            
            # 로그인 폼 요소 대기 및 찾기
            wait = WebDriverWait(self.driver, 10)
            
            # 사용자명 입력 필드 찾기 (user_login)
            self.log_message("로그인 폼을 찾고 있습니다...")
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "user_login"))
            )
            
            # 비밀번호 입력 필드 찾기 (user_pass)
            password_field = self.driver.find_element(By.ID, "user_pass")
            
            # 로그인 버튼 찾기 (wp-submit)
            login_button = self.driver.find_element(By.ID, "wp-submit")
            
            self.log_message("로그인 정보를 입력하고 있습니다...")
            
            # 입력 필드 클리어 후 입력
            username_field.clear()
            username_field.send_keys(username)
            
            password_field.clear()
            password_field.send_keys(password)
            
            # 잠시 대기
            time.sleep(1)
            
            # 로그인 버튼 클릭
            self.log_message("로그인 버튼을 클릭합니다...")
            login_button.click()
            
            # 로그인 결과 확인
            time.sleep(3)
            
            # 로그인 성공 여부 확인
            if "wp-admin" in self.driver.current_url and "wp-login.php" not in self.driver.current_url:
                self.log_message("✅ 로그인에 성공했습니다!")
                self.is_logged_in = True
                
                # UI 업데이트
                self.root.after(0, self.on_login_success)
                
                # 자동으로 글 추가 페이지로 이동
                self.navigate_to_add_post()
            else:
                # 에러 메시지 확인
                error_elements = self.driver.find_elements(By.CLASS_NAME, "error")
                if error_elements:
                    error_text = error_elements[0].text
                    self.log_message(f"❌ 로그인 실패: {error_text}")
                else:
                    self.log_message("❌ 로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.")
                
                self.root.after(0, self.on_login_failure)
                
        except TimeoutException:
            self.log_message("❌ 페이지 로드 시간이 초과되었습니다. 네트워크 연결을 확인해주세요.")
            self.root.after(0, self.on_login_failure)
            
        except NoSuchElementException as e:
            self.log_message(f"❌ 로그인 폼을 찾을 수 없습니다. WordPress 사이트가 맞는지 확인해주세요.")
            self.root.after(0, self.on_login_failure)
            
        except WebDriverException as e:
            self.log_message(f"❌ 브라우저 오류: {str(e)}")
            self.root.after(0, self.on_login_failure)
            
        except Exception as e:
            self.log_message(f"❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
            self.root.after(0, self.on_login_failure)
    
    def on_login_success(self):
        """로그인 성공 시 UI 업데이트"""
        self.status_var.set("로그인 성공 - 글 추가 페이지로 이동 중...")
        self.login_button.config(state='normal')
        self.logout_button.config(state='normal')
        self.open_browser_button.config(state='normal')
        
    def on_login_failure(self):
        """로그인 실패 시 UI 업데이트"""
        self.status_var.set("로그인 실패")
        self.login_button.config(state='normal')
        self.logout_button.config(state='disabled')
        self.open_browser_button.config(state='disabled')
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def logout(self):
        """로그아웃을 수행합니다."""
        if self.driver:
            try:
                self.log_message("로그아웃 중...")
                self.driver.quit()
                self.log_message("✅ 로그아웃 완료")
            except Exception as e:
                self.log_message(f"로그아웃 중 오류: {str(e)}")
            finally:
                self.driver = None
                self.is_logged_in = False
        
        # UI 상태 초기화
        self.status_var.set("준비됨")
        self.login_button.config(state='normal')
        self.logout_button.config(state='disabled')
        self.open_browser_button.config(state='disabled')
    
    def open_in_browser(self):
        """현재 페이지를 기본 브라우저에서 엽니다."""
        if self.driver and self.is_logged_in:
            try:
                current_url = self.driver.current_url
                import webbrowser
                webbrowser.open(current_url)
                self.log_message(f"기본 브라우저에서 열었습니다: {current_url}")
            except Exception as e:
                self.log_message(f"브라우저 열기 실패: {str(e)}")
        else:
            messagebox.showwarning("경고", "먼저 로그인을 해주세요.")
    
    def navigate_to_add_post(self):
        """글 추가 페이지로 이동하는 실제 작업을 수행합니다."""
        try:
            self.log_message("글 메뉴를 찾고 있습니다...")
            
            wait = WebDriverWait(self.driver, 10)
            
            # "글" 메뉴 찾기 (wp-menu-name 클래스)
            # 여러 가지 방법으로 글 메뉴를 찾아봅니다
            posts_menu = None
            
            # 방법 1: wp-menu-name 클래스를 가진 요소 중에서 "글"이 포함된 것 찾기
            try:
                menu_items = self.driver.find_elements(By.CLASS_NAME, "wp-menu-name")
                for item in menu_items:
                    if "글" in item.text or "Posts" in item.text:
                        posts_menu = item
                        break
            except:
                pass
            
            # 방법 2: 링크 텍스트로 찾기
            if not posts_menu:
                try:
                    posts_menu = self.driver.find_element(By.PARTIAL_LINK_TEXT, "글")
                except:
                    try:
                        posts_menu = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Posts")
                    except:
                        pass
            
            # 방법 3: CSS 선택자로 찾기
            if not posts_menu:
                try:
                    posts_menu = self.driver.find_element(By.CSS_SELECTOR, "a[href*='edit.php']")
                except:
                    pass
            
            if not posts_menu:
                self.log_message("❌ '글' 메뉴를 찾을 수 없습니다.")
                return
            
            # 글 메뉴 클릭
            self.log_message("'글' 메뉴를 클릭합니다...")
            self.driver.execute_script("arguments[0].click();", posts_menu)
            
            # 페이지 로드 대기
            time.sleep(2)
            
            # "글 추가" 버튼 찾기 (page-title-action 클래스)
            self.log_message("'글 추가' 버튼을 찾고 있습니다...")
            
            add_new_button = None
            
            # 방법 1: page-title-action 클래스로 찾기
            try:
                add_new_button = wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "page-title-action"))
                )
            except:
                pass
            
            # 방법 2: 링크 텍스트로 찾기
            if not add_new_button:
                try:
                    add_new_button = self.driver.find_element(By.PARTIAL_LINK_TEXT, "새로 추가")
                except:
                    try:
                        add_new_button = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Add New")
                    except:
                        pass
            
            # 방법 3: CSS 선택자로 찾기
            if not add_new_button:
                try:
                    add_new_button = self.driver.find_element(By.CSS_SELECTOR, "a[href*='post-new.php']")
                except:
                    pass
            
            if not add_new_button:
                self.log_message("❌ '글 추가' 버튼을 찾을 수 없습니다.")
                return
            
            # 글 추가 버튼 클릭
            self.log_message("'글 추가' 버튼을 클릭합니다...")
            self.driver.execute_script("arguments[0].click();", add_new_button)
            
            # 페이지 로드 대기
            time.sleep(3)
            
            # 성공 확인
            if "post-new.php" in self.driver.current_url or "wp-admin" in self.driver.current_url:
                self.log_message("✅ 글 작성 페이지로 이동했습니다!")
                self.root.after(0, lambda: self.status_var.set("글 작성 중..."))
                
                # 글 작성 전체 프로세스 시작
                self.start_post_writing_process()
            else:
                self.log_message("❌ 글 작성 페이지로 이동하지 못했습니다.")
                self.root.after(0, lambda: self.status_var.set("페이지 이동 실패"))
                
        except TimeoutException:
            self.log_message("❌ 페이지 로드 시간이 초과되었습니다.")
            
        except NoSuchElementException:
            self.log_message("❌ 필요한 요소를 찾을 수 없습니다. WordPress 관리자 권한을 확인해주세요.")
            
        except Exception as e:
            self.log_message(f"❌ 글 추가 페이지 이동 중 오류가 발생했습니다: {str(e)}")
    
    def start_post_writing_process(self):
        """글 작성 전체 프로세스를 관리합니다."""
        try:
            # 1단계: 텍스트 파일에서 데이터 읽기
            if not self.load_post_data():
                return
                
            # 2단계: 페이지 로드 완료 대기
            self.wait_for_page_load()
            
            # 3단계: 제목 입력
            if not self.input_post_title():
                return
                
            # 4단계: HTML 블록 추가 및 내용 입력
            if not self.add_html_block_and_content():
                return
                
            # 5단계: 편집 완료 처리
            self.finish_post_editing()
            
        except Exception as e:
            self.log_message(f"❌ 글 작성 프로세스 중 오류: {str(e)}")
            self.root.after(0, lambda: self.status_var.set("글 작성 실패"))
    
    def load_post_data(self):
        """텍스트 파일에서 제목과 내용을 로드합니다."""
        try:
            self.post_title, self.post_content = self.get_post_data()
            if not self.post_title or not self.post_content:
                self.log_message("❌ 텍스트 파일에서 데이터를 가져올 수 없습니다.")
                self.root.after(0, lambda: self.status_var.set("파일 읽기 실패"))
                return False
            
            self.log_message(f"✅ 글 데이터 로드 완료 - 제목: {self.post_title[:30]}...")
            return True
            
        except Exception as e:
            self.log_message(f"❌ 글 데이터 로드 실패: {str(e)}")
            return False
    
    def wait_for_page_load(self):
        """페이지가 완전히 로드될 때까지 대기합니다."""
        self.log_message("📝 페이지 로드 완료를 기다립니다...")
        time.sleep(5)  # 기본 대기
        
        # 에디터가 로드될 때까지 대기
        try:
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".block-editor-writing-flow, .editor-styles-wrapper")))
            self.log_message("✅ 에디터 로드 완료")
        except:
            self.log_message("⚠️ 에디터 로드 확인 실패, 계속 진행합니다.")
    
    def input_post_title(self):
        """글 제목을 입력합니다."""
        self.log_message("📝 제목을 입력합니다...")
        
        try:
            # 제목 입력 필드 찾기
            title_selectors = [
                ".wp-block-post-title .block-editor-rich-text__editable",
                ".editor-post-title__input",
                ".wp-block-post-title",
                "h1[data-title]",
                ".block-editor-rich-text__editable[aria-label*='제목'], .block-editor-rich-text__editable[aria-label*='title']"
            ]
            
            title_field = None
            for selector in title_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            title_field = element
                            self.log_message(f"✅ 제목 필드 찾음: {selector}")
                            break
                    if title_field:
                        break
                except:
                    continue
            
            if not title_field:
                self.log_message("❌ 제목 입력 필드를 찾을 수 없습니다.")
                return False
            
            # 제목 입력
            self.driver.execute_script("arguments[0].focus();", title_field)
            time.sleep(1)
            title_field.clear()
            title_field.send_keys(self.post_title)
            time.sleep(2)
            
            self.log_message(f"✅ 제목 입력 완료: {self.post_title}")
            return True
            
        except Exception as e:
            self.log_message(f"❌ 제목 입력 실패: {str(e)}")
            return False
    
    def add_html_block_and_content(self):
        """HTML 블록을 추가하고 내용을 입력합니다."""
        try:
            # 1단계: 본문 영역 클릭
            if not self.click_content_area():
                return False
                
            # 2단계: 블록 추가 버튼 클릭
            if not self.click_add_block_button():
                return False
                
            # 3단계: HTML 블록 검색 및 선택
            if not self.search_and_select_html_block():
                return False
                
            # 4단계: HTML 내용 입력
            if not self.input_html_content():
                return False
                
            return True
            
        except Exception as e:
            self.log_message(f"❌ HTML 블록 추가 실패: {str(e)}")
            return False
    
    def click_content_area(self):
        """본문 영역을 클릭합니다."""
        self.log_message("📝 본문 영역을 클릭합니다...")
        
        try:
            content_selectors = [
                ".block-editor-writing-flow",
                ".wp-block",
                ".block-editor-block-list__layout",
                ".editor-styles-wrapper"
            ]
            
            for selector in content_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        self.driver.execute_script("arguments[0].click();", element)
                        time.sleep(2)
                        self.log_message(f"✅ 본문 영역 클릭 완료: {selector}")
                        return True
                except:
                    continue
                    
            self.log_message("❌ 본문 영역을 찾을 수 없습니다.")
            return False
            
        except Exception as e:
            self.log_message(f"❌ 본문 영역 클릭 실패: {str(e)}")
            return False
    
    def click_add_block_button(self):
        """블록 추가 버튼을 클릭합니다."""
        self.log_message("📝 블록 추가 버튼을 클릭합니다...")
        
        try:
            add_block_selectors = [
                ".block-editor-inserter__toggle",
                ".block-editor-button-block-appender",
                "[aria-label*='블록 추가'], [aria-label*='Add block']",
                ".components-button.has-icon"
            ]
            
            for selector in add_block_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            self.driver.execute_script("arguments[0].click();", element)
                            time.sleep(3)
                            self.log_message(f"✅ 블록 추가 버튼 클릭 완료: {selector}")
                            return True
                except:
                    continue
            
            # 대안: 키보드 단축키 사용
            self.log_message("📝 키보드 단축키로 블록 추가를 시도합니다...")
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ENTER).perform()
            time.sleep(2)
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ 블록 추가 버튼 클릭 실패: {str(e)}")
            return False
    
    def search_and_select_html_block(self):
        """HTML 블록을 검색하고 선택합니다."""
        self.log_message("📝 HTML 블록을 검색합니다...")
        
        try:
            # 검색창 찾기 및 'html' 입력
            search_selectors = [
                "input[placeholder*='검색'], input[placeholder*='Search']",
                ".components-search-control__input",
                ".block-editor-inserter__search input"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            search_input = element
                            break
                    if search_input:
                        break
                except:
                    continue
            
            if search_input:
                self.driver.execute_script("arguments[0].focus();", search_input)
                search_input.clear()
                search_input.send_keys("html")
                time.sleep(3)
                self.log_message("✅ 'html' 검색 완료")
            
            # HTML 블록 선택
            html_block_selectors = [
                ".block-editor-block-types-list__list-item",
                "button[aria-label*='HTML'], button[title*='HTML']"
            ]
            
            for selector in html_block_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.get_attribute('aria-label') or element.text or ''
                            if 'html' in element_text.lower():
                                self.driver.execute_script("arguments[0].click();", element)
                                time.sleep(3)
                                self.log_message("✅ HTML 블록 선택 완료")
                                return True
                except:
                    continue
            
            # XPath로 텍스트 기반 검색
            try:
                html_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'HTML')]")
                self.driver.execute_script("arguments[0].click();", html_button)
                time.sleep(3)
                self.log_message("✅ HTML 블록 선택 완료 (XPath)")
                return True
            except:
                pass
            
            self.log_message("❌ HTML 블록을 찾을 수 없습니다.")
            return False
            
        except Exception as e:
            self.log_message(f"❌ HTML 블록 검색 실패: {str(e)}")
            return False
    
    def input_html_content(self):
        """HTML 내용을 입력합니다."""
        self.log_message("📝 HTML 내용을 입력합니다...")
        
        try:
            time.sleep(3)  # HTML 블록 로드 대기
            
            # HTML textarea 찾기
            html_textarea = None
            textarea_selectors = [
                ".wp-block[data-type='core/html'] textarea",
                ".wp-block-html textarea",
                "textarea[aria-label*='HTML']"
            ]
            
            # 일반적인 textarea 중에서 HTML 블록용 찾기
            all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            self.log_message(f"📝 전체 textarea 개수: {len(all_textareas)}")
            
            # 가장 최근에 추가된 textarea (HTML 블록용) 선택
            for textarea in reversed(all_textareas):
                if textarea.is_displayed() and textarea.is_enabled():
                    # 제목 필드가 아닌지 확인
                    parent_html = self.driver.execute_script("return arguments[0].parentElement.innerHTML;", textarea)
                    if 'title' not in parent_html.lower():
                        html_textarea = textarea
                        self.log_message("✅ HTML textarea 발견")
                        break
            
            if not html_textarea:
                self.log_message("❌ HTML textarea를 찾을 수 없습니다.")
                return False
            
            # 내용 입력 (여러 방법 시도)
            input_success = False
            input_methods = [
                ("send_keys", lambda: (html_textarea.clear(), html_textarea.send_keys(self.post_content))),
                ("javascript", lambda: self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", html_textarea, self.post_content)),
                ("clipboard", lambda: self.paste_via_clipboard(html_textarea))
            ]
            
            for method_name, method_func in input_methods:
                try:
                    self.log_message(f"📝 {method_name} 방법으로 입력 시도...")
                    self.driver.execute_script("arguments[0].focus();", html_textarea)
                    time.sleep(1)
                    
                    if method_name == "send_keys":
                        html_textarea.clear()
                        html_textarea.send_keys(self.post_content)
                    elif method_name == "javascript":
                        self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input'));", html_textarea, self.post_content)
                    elif method_name == "clipboard":
                        self.paste_via_clipboard(html_textarea)
                    
                    time.sleep(2)
                    
                    # 입력 확인
                    current_value = html_textarea.get_attribute('value') or ''
                    if self.post_content[:50] in current_value:
                        self.log_message(f"✅ {method_name} 방법으로 입력 성공")
                        input_success = True
                        break
                    
                except Exception as e:
                    self.log_message(f"❌ {method_name} 방법 실패: {str(e)}")
                    continue
            
            if input_success:
                # HTML 내용 입력 완료 후 키보드 시퀀스 실행
                self.log_message("📝 HTML 내용 입력 완료, 키보드 시퀀스 실행...")
                time.sleep(2)  # 입력 완료 후 충분한 대기
                
                try:
                    from selenium.webdriver.common.keys import Keys
                    from selenium.webdriver.common.action_chains import ActionChains
                    
                    # 현재 활성 요소에 포커스 확인
                    active_element = self.driver.switch_to.active_element
                    self.log_message(f"📝 현재 활성 요소: {active_element.tag_name}")
                    
                    # 방법 1: ActionChains를 사용한 키 입력
                    try:
                        self.log_message("📝 방법 1: ActionChains로 키 시퀀스 실행...")
                        
                        actions = ActionChains(self.driver)
                        actions.send_keys(Keys.TAB)
                        actions.pause(1)
                        actions.send_keys(Keys.TAB)  
                        actions.pause(1)
                        actions.send_keys(Keys.ENTER)
                        actions.perform()
                        
                        time.sleep(2)
                        self.log_message("✅ 방법 1 완료 (ActionChains)")
                        
                    except Exception as e1:
                        self.log_message(f"❌ 방법 1 실패: {str(e1)}")
                        
                        # 방법 2: 개별 키 입력
                        try:
                            self.log_message("📝 방법 2: 개별 키 입력...")
                            
                            # TAB 키 첫 번째
                            html_textarea.send_keys(Keys.TAB)
                            time.sleep(1)
                            self.log_message("✅ TAB 키 1회 완료")
                            
                            # TAB 키 두 번째
                            self.driver.switch_to.active_element.send_keys(Keys.TAB)
                            time.sleep(1)
                            self.log_message("✅ TAB 키 2회 완료")
                            
                            # ENTER 키
                            self.driver.switch_to.active_element.send_keys(Keys.ENTER)
                            time.sleep(1)
                            self.log_message("✅ ENTER 키 완료")
                            
                        except Exception as e2:
                            self.log_message(f"❌ 방법 2 실패: {str(e2)}")
                            
                            # 방법 3: body 요소를 통한 키 입력
                            try:
                                self.log_message("📝 방법 3: body 요소를 통한 키 입력...")
                                
                                body = self.driver.find_element(By.TAG_NAME, "body")
                                
                                body.send_keys(Keys.TAB)
                                time.sleep(1)
                                self.log_message("✅ body TAB 키 1회")
                                
                                body.send_keys(Keys.TAB)
                                time.sleep(1)
                                self.log_message("✅ body TAB 키 2회")
                                
                                body.send_keys(Keys.ENTER)
                                time.sleep(1)
                                self.log_message("✅ body ENTER 키")
                                
                            except Exception as e3:
                                self.log_message(f"❌ 방법 3도 실패: {str(e3)}")
                                
                                # 방법 4: JavaScript 키 이벤트
                                try:
                                    self.log_message("📝 방법 4: JavaScript 키 이벤트...")
                                    
                                    # TAB 키 이벤트 2번
                                    for i in range(2):
                                        self.driver.execute_script("""
                                            var event = new KeyboardEvent('keydown', {
                                                key: 'Tab',
                                                code: 'Tab',
                                                keyCode: 9,
                                                bubbles: true
                                            });
                                            document.activeElement.dispatchEvent(event);
                                            
                                            var event2 = new KeyboardEvent('keyup', {
                                                key: 'Tab',
                                                code: 'Tab', 
                                                keyCode: 9,
                                                bubbles: true
                                            });
                                            document.activeElement.dispatchEvent(event2);
                                        """)
                                        time.sleep(1)
                                        self.log_message(f"✅ JavaScript TAB 키 {i+1}회")
                                    
                                    # ENTER 키 이벤트
                                    self.driver.execute_script("""
                                        var event = new KeyboardEvent('keydown', {
                                            key: 'Enter',
                                            code: 'Enter',
                                            keyCode: 13,
                                            bubbles: true
                                        });
                                        document.activeElement.dispatchEvent(event);
                                        
                                        var event2 = new KeyboardEvent('keyup', {
                                            key: 'Enter',
                                            code: 'Enter',
                                            keyCode: 13,
                                            bubbles: true
                                        });
                                        document.activeElement.dispatchEvent(event2);
                                    """)
                                    time.sleep(1)
                                    self.log_message("✅ JavaScript ENTER 키")
                                    
                                except Exception as e4:
                                    self.log_message(f"❌ 방법 4도 실패: {str(e4)}")
                    
                    self.log_message("✅ 키보드 시퀀스 시도 완료")
                    
                except Exception as e:
                    self.log_message(f"❌ 키보드 시퀀스 전체 실패: {str(e)}")
            
            return input_success
            
        except Exception as e:
            self.log_message(f"❌ HTML 내용 입력 실패: {str(e)}")
            return False
    
    def paste_via_clipboard(self, element):
        """클립보드를 통한 붙여넣기"""
        try:
            import subprocess
            subprocess.run(['clip'], input=self.post_content, text=True, check=True)
            time.sleep(0.5)
            
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
        except:
            pass
    
    def finish_post_editing(self):
        """편집 완료 처리를 합니다."""
        self.log_message("📝 키보드 입력으로 편집을 완료합니다...")
        
        try:
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains
            
            # TAB 키 두 번, ENTER 키 한 번 시퀀스
            actions = ActionChains(self.driver)
            
            # 1단계: TAB 키 첫 번째
            self.log_message("📝 TAB 키 첫 번째 입력...")
            actions.send_keys(Keys.TAB)
            actions.perform()
            time.sleep(1)
            
            # 2단계: TAB 키 두 번째  
            self.log_message("📝 TAB 키 두 번째 입력...")
            actions = ActionChains(self.driver)  # 새로운 액션 체인 생성
            actions.send_keys(Keys.TAB)
            actions.perform()
            time.sleep(1)
            
            # 3단계: ENTER 키
            self.log_message("📝 ENTER 키 입력...")
            actions = ActionChains(self.driver)  # 새로운 액션 체인 생성
            actions.send_keys(Keys.ENTER)
            actions.perform()
            time.sleep(2)
            
            self.log_message("✅ 키보드 시퀀스 완료 (TAB → TAB → ENTER)")
            
            # 최종 완료
            self.root.after(0, lambda: self.status_var.set("글 작성 완료"))
            self.log_message("🎉 모든 작업이 완료되었습니다!")
            
        except Exception as e:
            self.log_message(f"❌ 키보드 시퀀스 실행 실패: {str(e)}")
            
            # 대안: Escape 키 사용
            try:
                self.log_message("📝 대안으로 Escape 키를 사용합니다...")
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.ESCAPE)
                actions.perform()
                time.sleep(1)
                self.log_message("✅ Escape 키로 편집 완료")
                
                # 최종 완료
                self.root.after(0, lambda: self.status_var.set("글 작성 완료"))
                self.log_message("🎉 모든 작업이 완료되었습니다!")
                
            except Exception as e2:
                self.log_message(f"❌ 대안 방법도 실패: {str(e2)}")
                self.root.after(0, lambda: self.status_var.set("편집 완료 실패"))
    
    def click_html_block_button(self):
        """HTML 블록 버튼을 클릭합니다."""
        try:
            button_selectors = [
                "button.components-button.block-editor-block-types-list__item.editor-block-list-item-html.is-next-40px-default-size",
                "button.components-button.block-editor-block-types-list__item.editor-block-list-item-html",
                "button[class*='editor-block-list-item-html']"
            ]
            
            for selector in button_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element_class = element.get_attribute('class') or ''
                            if 'html' in element_class.lower():
                                self.driver.execute_script("arguments[0].click();", element)
                                time.sleep(2)
                                return True
                except:
                    continue
            
            return False
            
        except:
            return False
    
    def fill_post_content(self):
        """레거시 호환성을 위한 함수 (새로운 함수로 리다이렉트)"""
        self.start_post_writing_process()
        
    def old_fill_post_content_backup(self):
        """이전 버전의 백업 (사용 안 함)"""
        try:
            # 텍스트 파일에서 제목과 내용 가져오기
            title, content = self.get_post_data()
            if not title or not content:
                self.log_message("❌ 텍스트 파일에서 데이터를 가져올 수 없습니다.")
                return
            
            wait = WebDriverWait(self.driver, 15)
            time.sleep(3)  # 페이지 로드 대기
            
            # 1. 제목 입력
            self.log_message("📝 제목을 입력하고 있습니다...")
            
            # 제목 입력 필드 찾기
            title_field = None
            title_selectors = [
                "wp-block.wp-block-post-title.block-editor-block-list__block.editor-post-title.editor-post-title__input.rich-text",
                ".editor-post-title__input",
                ".wp-block-post-title",
                "h1[data-title]",
                ".block-editor-rich-text__editable"
            ]
            
            for selector in title_selectors:
                try:
                    if selector.startswith('.'):
                        title_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    else:
                        title_field = self.driver.find_element(By.CSS_SELECTOR, f".{selector.replace(' ', '.')}")
                    break
                except:
                    continue
            
            if title_field:
                self.driver.execute_script("arguments[0].click();", title_field)
                time.sleep(1)
                title_field.clear()
                title_field.send_keys(title)
                self.log_message(f"✅ 제목 입력 완료: {title}")
            else:
                self.log_message("❌ 제목 입력 필드를 찾을 수 없습니다.")
            
            time.sleep(2)
            
            # 2. 본문 영역 클릭 (block-editor-plain-text)
            self.log_message("📝 본문 영역을 클릭하고 있습니다...")
            
            # 먼저 페이지가 완전히 로드될 때까지 기다림
            time.sleep(5)
            
            # 다양한 방법으로 본문 영역 찾기
            content_area = None
            content_selectors = [
                ".block-editor-writing-flow",
                ".wp-block",
                ".block-editor-block-list__layout",
                ".editor-styles-wrapper",
                "[data-type='core/paragraph']",
                ".wp-block-paragraph"
            ]
            
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        content_area = elements[0]
                        self.log_message(f"✅ 본문 영역 찾음: {selector}")
                        break
                except:
                    continue
            
            if content_area:
                # 본문 영역을 클릭하여 포커스 맞추기
                self.driver.execute_script("arguments[0].scrollIntoView(true);", content_area)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", content_area)
                time.sleep(2)
                self.log_message("✅ 본문 영역 클릭 완료")
            else:
                self.log_message("❌ 본문 영역을 찾을 수 없습니다.")
            
            # 3. + 버튼 찾기 및 클릭 (여러 방법 시도)
            self.log_message("📝 블록 추가 버튼(+)을 찾고 있습니다...")
            
            add_block_btn = None
            add_block_selectors = [
                ".block-editor-inserter__toggle",
                ".block-editor-button-block-appender",
                "[aria-label*='블록 추가'], [aria-label*='Add block']",
                ".components-button.has-icon",
                ".block-editor-block-list__empty-block-inserter",
                "[data-testid='block-inserter-toggle']"
            ]
            
            for selector in add_block_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            add_block_btn = element
                            self.log_message(f"✅ 블록 추가 버튼 찾음: {selector}")
                            break
                    if add_block_btn:
                        break
                except:
                    continue
            
            # 키보드 단축키로 블록 추가 시도
            if not add_block_btn:
                self.log_message("⚠️ + 버튼을 찾을 수 없어 키보드 단축키를 사용합니다...")
                try:
                    from selenium.webdriver.common.keys import Keys
                    from selenium.webdriver.common.action_chains import ActionChains
                    
                    # 에디터 영역에 포커스를 맞추고 Enter로 새 블록 생성
                    actions = ActionChains(self.driver)
                    actions.send_keys(Keys.ENTER).perform()
                    time.sleep(2)
                    
                    # Ctrl+Shift+Alt+I로 블록 삽입기 열기
                    actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).key_down(Keys.ALT).send_keys('i').key_up(Keys.ALT).key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
                    time.sleep(2)
                    self.log_message("✅ 키보드 단축키로 블록 삽입기 열기 시도")
                except Exception as e:
                    self.log_message(f"❌ 키보드 단축키 실패: {str(e)}")
            else:
                # + 버튼 클릭
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", add_block_btn)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", add_block_btn)
                    time.sleep(3)
                    self.log_message("✅ 블록 추가 버튼 클릭 완료")
                except Exception as e:
                    self.log_message(f"❌ 블록 추가 버튼 클릭 실패: {str(e)}")
            
            time.sleep(3)
            
            # 4. 검색 입력란에 'html' 입력 (더 넓은 범위로 검색)
            self.log_message("📝 'html' 블록을 검색하고 있습니다...")
            
            search_input = None
            search_selectors = [
                "input[placeholder*='검색'], input[placeholder*='Search']",
                ".components-search-control__input",
                ".block-editor-inserter__search input",
                ".components-input-control__input",
                "input[type='search']",
                ".block-editor-inserter__search-input"
            ]
            
            # 검색창이 나타날 때까지 잠시 대기
            time.sleep(2)
            
            for selector in search_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            search_input = element
                            self.log_message(f"✅ 검색창 찾음: {selector}")
                            break
                    if search_input:
                        break
                except:
                    continue
            
            if search_input:
                try:
                    self.driver.execute_script("arguments[0].focus();", search_input)
                    time.sleep(1)
                    search_input.clear()
                    search_input.send_keys("html")
                    time.sleep(3)
                    self.log_message("✅ 'html' 검색 완료")
                except Exception as e:
                    self.log_message(f"❌ 검색 입력 실패: {str(e)}")
                    return
            else:
                self.log_message("❌ 검색 입력란을 찾을 수 없습니다.")
                # 검색창이 없다면 직접 HTML 블록을 찾아보기
                self.log_message("📝 직접 HTML 블록을 찾고 있습니다...")
            
            # 5. HTML 블록 선택 (더 다양한 방법으로 시도)
            self.log_message("📝 HTML 블록을 선택하고 있습니다...")
            
            html_block = None
            html_block_selectors = [
                ".block-editor-block-types-list__list-item",
                "[data-id='core/html']",
                "button[aria-label*='HTML'], button[title*='HTML']",
                ".editor-block-list-item-html",
                ".components-button:contains('HTML')"
            ]
            
            time.sleep(2)
            
            for selector in html_block_selectors:
                try:
                    if "contains" in selector:
                        # XPath를 사용하여 텍스트로 찾기
                        elements = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'HTML')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            html_block = element
                            self.log_message(f"✅ HTML 블록 찾음: {selector}")
                            break
                    if html_block:
                        break
                except:
                    continue
            
            if html_block:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", html_block)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", html_block)
                    time.sleep(3)
                    self.log_message("✅ HTML 블록 선택 완료")
                except Exception as e:
                    self.log_message(f"❌ HTML 블록 클릭 실패: {str(e)}")
                    return
            else:
                self.log_message("❌ HTML 블록을 찾을 수 없습니다.")
                return
            
            # 6. HTML 내용 입력 (제목과 겹치지 않는 영역 찾기)
            self.log_message("📝 HTML 블록의 입력 영역을 찾고 있습니다...")
            
            # HTML 블록이 완전히 로드될 때까지 충분히 대기
            time.sleep(5)
            
            # 현재 페이지의 모든 textarea 확인
            all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            self.log_message(f"📝 페이지에서 찾은 textarea 개수: {len(all_textareas)}")
            
            html_input = None
            
            # HTML 블록 전용 textarea 찾기 (가장 확실한 방법)
            html_block_selectors = [
                ".wp-block[data-type='core/html'] textarea",
                ".wp-block-html textarea",
                "div[data-type='core/html'] textarea"
            ]
            
            for selector in html_block_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        html_input = elements[0]  # 첫 번째 HTML 블록의 textarea
                        self.log_message(f"✅ HTML 블록 textarea 찾음: {selector}")
                        break
                except Exception as e:
                    continue
            
            # HTML 블록을 찾지 못했다면 다른 방법 시도
            if not html_input:
                self.log_message("📝 일반적인 방법으로 HTML 입력 영역을 찾고 있습니다...")
                
                # 모든 textarea를 순회하며 적합한 것 찾기
                for i, textarea in enumerate(all_textareas):
                    try:
                        if not textarea.is_displayed() or not textarea.is_enabled():
                            continue
                            
                        # textarea의 정보 수집
                        element_info = self.driver.execute_script("""
                            var elem = arguments[0];
                            var rect = elem.getBoundingClientRect();
                            return {
                                className: elem.className,
                                placeholder: elem.placeholder || '',
                                id: elem.id || '',
                                value: elem.value || '',
                                top: rect.top,
                                height: rect.height,
                                index: arguments[1]
                            };
                        """, textarea, i)
                        
                        self.log_message(f"📝 Textarea {i}: {element_info}")
                        
                        # 제목 필드가 아닌 경우 선택 (높이가 더 크거나, 아래쪽에 위치)
                        is_title = ('title' in element_info.get('className', '').lower() or 
                                  'title' in element_info.get('placeholder', '').lower() or
                                  'title' in element_info.get('id', '').lower())
                        
                        if not is_title:
                            html_input = textarea
                            self.log_message(f"✅ 적합한 textarea 선택 (인덱스: {i})")
                            break
                            
                    except Exception as e:
                        self.log_message(f"Textarea {i} 검사 중 오류: {str(e)}")
                        continue
                
                # 여전히 찾지 못했다면 가장 마지막 textarea 사용
                if not html_input and all_textareas:
                    html_input = all_textareas[-1]
                    self.log_message("📝 마지막 textarea를 사용합니다.")
            
            if html_input:
                try:
                    # HTML 입력 영역으로 스크롤하고 포커스
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", html_input)
                    time.sleep(3)
                    
                    # 현재 입력 영역의 정보 로깅
                    element_info = self.driver.execute_script("""
                        var elem = arguments[0];
                        return {
                            tagName: elem.tagName,
                            className: elem.className,
                            placeholder: elem.placeholder || '',
                            value: elem.value || '',
                            id: elem.id || '',
                            readOnly: elem.readOnly,
                            disabled: elem.disabled
                        };
                    """, html_input)
                    self.log_message(f"📝 선택된 입력 영역 상세 정보: {element_info}")
                    
                    # 입력 가능한 상태인지 확인
                    if element_info.get('readOnly') or element_info.get('disabled'):
                        self.log_message("❌ 입력 영역이 읽기 전용이거나 비활성화되어 있습니다.")
                        # 다른 textarea 찾기
                        other_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                        for textarea in other_textareas:
                            if textarea != html_input and textarea.is_displayed() and textarea.is_enabled():
                                if not textarea.get_attribute('readOnly') and not textarea.get_attribute('disabled'):
                                    html_input = textarea
                                    self.log_message("✅ 다른 활성화된 textarea로 변경")
                                    break
                    
                    # 여러 가지 방법으로 내용 입력 시도
                    input_methods = [
                        "selenium_send_keys",
                        "javascript_value",
                        "javascript_innerHTML", 
                        "clipboard_paste"
                    ]
                    
                    content_inserted = False
                    
                    for method in input_methods:
                        try:
                            self.log_message(f"📝 입력 방법 시도: {method}")
                            
                            # 포커스 맞추기
                            self.driver.execute_script("arguments[0].focus();", html_input)
                            self.driver.execute_script("arguments[0].click();", html_input)
                            time.sleep(1)
                            
                            if method == "selenium_send_keys":
                                # 방법 1: Selenium send_keys
                                html_input.clear()
                                time.sleep(0.5)
                                html_input.send_keys(content)
                                
                            elif method == "javascript_value":
                                # 방법 2: JavaScript로 value 직접 설정
                                self.driver.execute_script("arguments[0].value = arguments[1];", html_input, content)
                                # input 이벤트 트리거
                                self.driver.execute_script("""
                                    var elem = arguments[0];
                                    elem.dispatchEvent(new Event('input', {bubbles: true}));
                                    elem.dispatchEvent(new Event('change', {bubbles: true}));
                                """, html_input)
                                
                            elif method == "javascript_innerHTML":
                                # 방법 3: innerHTML 설정 (contenteditable인 경우)
                                self.driver.execute_script("arguments[0].innerHTML = arguments[1];", html_input, content)
                                
                            elif method == "clipboard_paste":
                                # 방법 4: 클립보드를 통한 붙여넣기
                                from selenium.webdriver.common.keys import Keys
                                from selenium.webdriver.common.action_chains import ActionChains
                                
                                # 클립보드에 내용 복사 (Windows)
                                import subprocess
                                try:
                                    subprocess.run(['clip'], input=content, text=True, check=True)
                                    time.sleep(0.5)
                                    
                                    # Ctrl+V로 붙여넣기
                                    actions = ActionChains(self.driver)
                                    actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                                except:
                                    continue
                            
                            time.sleep(2)
                            
                            # 입력 완료 확인
                            new_value = html_input.get_attribute('value') or html_input.get_attribute('innerHTML') or ''
                            if content[:50] in new_value:  # 내용의 처음 50자가 포함되어 있는지 확인
                                self.log_message(f"✅ {method} 방법으로 HTML 내용 입력 완료 ({len(content)}자)")
                                content_inserted = True
                                break
                            else:
                                self.log_message(f"❌ {method} 방법 실패 - 내용 확인: {new_value[:100]}...")
                                
                        except Exception as e:
                            self.log_message(f"❌ {method} 방법 오류: {str(e)}")
                            continue
                    
                    if content_inserted:
                        # HTML 블록 버튼 클릭하여 편집 모드 종료
                        self.log_message("📝 HTML 블록 버튼을 클릭하여 편집 모드를 종료합니다...")
                        try:
                            # 지정된 클래스의 버튼 찾기
                            html_button = None
                            button_selectors = [
                                # 정확한 클래스 매칭
                                "button.components-button.block-editor-block-types-list__item.editor-block-list-item-html.is-next-40px-default-size",
                                ".components-button.block-editor-block-types-list__item.editor-block-list-item-html.is-next-40px-default-size",
                                # 단계적 클래스 완화
                                "button.components-button.block-editor-block-types-list__item.editor-block-list-item-html",
                                ".components-button.block-editor-block-types-list__item.editor-block-list-item-html",
                                "button.editor-block-list-item-html",
                                ".editor-block-list-item-html",
                                "button.block-editor-block-types-list__item",
                                ".block-editor-block-types-list__item",
                                # 속성으로 찾기
                                "button[class*='editor-block-list-item-html']",
                                "button[class*='components-button'][class*='block-editor-block-types-list__item']"
                            ]
                            
                            for selector in button_selectors:
                                try:
                                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                    for element in elements:
                                        if element.is_displayed() and element.is_enabled():
                                            # 버튼의 클래스 정보 확인
                                            element_class = element.get_attribute('class') or ''
                                            element_text = element.text or ''
                                            aria_label = element.get_attribute('aria-label') or ''
                                            
                                            self.log_message(f"📝 버튼 후보 - 클래스: {element_class}")
                                            self.log_message(f"📝 버튼 후보 - 텍스트: {element_text}")
                                            
                                            # 지정된 핵심 클래스들이 포함되어 있는지 확인
                                            required_classes = [
                                                'components-button',
                                                'block-editor-block-types-list__item', 
                                                'editor-block-list-item-html'
                                            ]
                                            
                                            class_match_count = sum(1 for cls in required_classes if cls in element_class)
                                            
                                            # HTML 관련 키워드도 확인
                                            has_html_keyword = ('html' in element_class.lower() or 
                                                              'html' in element_text.lower() or 
                                                              'html' in aria_label.lower())
                                            
                                            if class_match_count >= 2 or has_html_keyword:
                                                html_button = element
                                                self.log_message(f"✅ HTML 버튼 찾음: {selector}")
                                                self.log_message(f"📝 매칭된 클래스 수: {class_match_count}/{len(required_classes)}")
                                                self.log_message(f"📝 HTML 키워드 포함: {has_html_keyword}")
                                                break
                                    
                                    if html_button:
                                        break
                                except Exception as e:
                                    self.log_message(f"선택자 {selector} 오류: {str(e)}")
                                    continue
                            
                            if html_button:
                                try:
                                    # 버튼으로 스크롤하고 클릭
                                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", html_button)
                                    time.sleep(1)
                                    
                                    # 클릭 시도 (여러 방법)
                                    click_methods = [
                                        # 방법 1: 기본 클릭
                                        lambda: html_button.click(),
                                        # 방법 2: JavaScript 클릭
                                        lambda: self.driver.execute_script("arguments[0].click();", html_button),
                                        # 방법 3: 이벤트 디스패치
                                        lambda: self.driver.execute_script("""
                                            var elem = arguments[0];
                                            var event = new MouseEvent('click', {
                                                view: window,
                                                bubbles: true,
                                                cancelable: true
                                            });
                                            elem.dispatchEvent(event);
                                        """, html_button),
                                        # 방법 4: 포커스 후 클릭
                                        lambda: (html_button.send_keys(''), html_button.click())
                                    ]
                                    
                                    clicked = False
                                    for i, click_method in enumerate(click_methods):
                                        try:
                                            if i == 3:  # 방법 4는 튜플 반환
                                                html_button.send_keys('')
                                                html_button.click()
                                            else:
                                                click_method()
                                            self.log_message(f"✅ HTML 버튼 클릭 완료 (방법 {i+1})")
                                            clicked = True
                                            break
                                        except Exception as e:
                                            self.log_message(f"❌ 클릭 방법 {i+1} 실패: {str(e)}")
                                            continue
                                    
                                    if not clicked:
                                        self.log_message("❌ 모든 클릭 방법이 실패했습니다.")
                                    
                                    time.sleep(2)
                                    
                                except Exception as e:
                                    self.log_message(f"❌ HTML 버튼 클릭 실패: {str(e)}")
                                    
                            else:
                                self.log_message("❌ 지정된 클래스의 HTML 버튼을 찾을 수 없습니다.")
                                # 대안: Escape 키 사용
                                try:
                                    from selenium.webdriver.common.keys import Keys
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    
                                    actions = ActionChains(self.driver)
                                    actions.send_keys(Keys.ESCAPE).perform()
                                    self.log_message("✅ 대안으로 Escape 키 사용")
                                    time.sleep(1)
                                except:
                                    pass
                                
                        except Exception as e:
                            self.log_message(f"❌ HTML 버튼 클릭 과정에서 오류: {str(e)}")
                        
                        # 완료 상태 업데이트
                        self.root.after(0, lambda: self.status_var.set("글 작성 완료"))
                        self.log_message("🎉 모든 작업이 완료되었습니다!")
                    else:
                        self.log_message("❌ 모든 입력 방법이 실패했습니다.")
                        # 대안 방법 시도
                        self.try_alternative_content_input(content)
                    
                except Exception as e:
                    self.log_message(f"❌ HTML 내용 입력 실패: {str(e)}")
                    self.try_alternative_content_input(content)
                    
            else:
                self.log_message("❌ HTML 입력 영역을 찾을 수 없습니다.")
                # 대안: 단계별로 다시 시도
                self.try_alternative_content_input(content)
                
        except TimeoutException:
            self.log_message("❌ 요소를 찾는 데 시간이 초과되었습니다.")
            
        except Exception as e:
            self.log_message(f"❌ 글 작성 중 오류가 발생했습니다: {str(e)}")
    
    def try_alternative_content_input(self, content):
        """대안 방법으로 내용을 입력합니다."""
        self.log_message("📝 대안 방법으로 내용을 입력합니다...")
        try:
            # 방법 1: 모든 편집 가능한 영역 찾기
            editable_areas = self.driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
            
            for area in editable_areas:
                if area.is_displayed() and area.is_enabled():
                    # 제목 영역이 아닌지 확인
                    area_text = area.get_attribute('innerHTML') or ''
                    area_class = area.get_attribute('class') or ''
                    
                    if 'title' not in area_class.lower() and len(area_text.strip()) == 0:
                        self.driver.execute_script("arguments[0].focus();", area)
                        self.driver.execute_script("arguments[0].innerHTML = arguments[1];", area, content)
                        self.log_message("✅ 편집 가능한 영역에 내용 입력 완료")
                        self.root.after(0, lambda: self.status_var.set("글 작성 완료 (대안 방법)"))
                        return
            
            # 방법 2: 새 단락 블록 추가
            self.log_message("📝 새 단락 블록을 추가합니다...")
            try:
                # Enter 키를 눌러 새 블록 생성
                from selenium.webdriver.common.keys import Keys
                body = self.driver.find_element(By.TAG_NAME, "body")
                body.send_keys(Keys.ENTER)
                time.sleep(2)
                
                # 새로 생성된 블록에 내용 입력
                new_blocks = self.driver.find_elements(By.CSS_SELECTOR, "p[data-empty='true'], .wp-block-paragraph")
                if new_blocks:
                    new_block = new_blocks[-1]  # 가장 마지막 블록
                    self.driver.execute_script("arguments[0].innerHTML = arguments[1];", new_block, content)
                    self.log_message("✅ 새 단락 블록에 내용 입력 완료")
                    self.root.after(0, lambda: self.status_var.set("글 작성 완료 (단락 블록)"))
                    return
                    
            except Exception as e:
                self.log_message(f"❌ 새 블록 생성 실패: {str(e)}")
            
            self.log_message("❌ 모든 대안 방법이 실패했습니다.")
            
        except Exception as e:
            self.log_message(f"❌ 대안 방법 실행 중 오류: {str(e)}")
    
    def on_closing(self):
        """프로그램 종료 시 정리 작업"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        self.root.destroy()


def main():
    """메인 함수"""
    root = tk.Tk()
    app = WordPressAutoLogin(root)
    
    # 창 닫기 이벤트 처리
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # GUI 시작
    root.mainloop()


if __name__ == "__main__":
    main()