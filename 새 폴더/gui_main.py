"""
자동 글 변환 프로그램 - GUI 버전
tkinter를 사용한 그래픽 사용자 인터페이스
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import threading
from typing import Optional, Dict, Any
import json
import os
from datetime import datetime

# 기존 모듈들 임포트
from gemini_api import GeminiAPI
from prompt_system import PromptSystem

class TextTransformGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🤖 자동 글 변환 프로그램")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # 아이콘 및 스타일 설정
        self.setup_style()
        
        # 백엔드 초기화
        self.gemini_api = None
        self.prompt_system = PromptSystem()
        self.current_guideline = None
        self.current_model = "gemini-2.5-pro"  # 사용자가 원하는 기본 모델
        
        # GUI 구성 요소 생성
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        
        # 초기화
        self.initialize_app()
    
    def setup_style(self):
        """스타일 및 테마 설정"""
        style = ttk.Style()
        
        # 사용 가능한 테마 중에서 선택
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # 커스텀 스타일 설정
        style.configure('Title.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Heading.TLabel', font=('Arial', 11, 'bold'))
        
        # 메인 윈도우 배경색
        self.root.configure(bg='#f0f0f0')
    
    def create_menu(self):
        """메뉴바 생성"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="결과 저장", command=self.save_result)
        file_menu.add_command(label="결과 불러오기", command=self.load_result)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)
        
        # 편집 메뉴
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="편집", menu=edit_menu)
        edit_menu.add_command(label="전체 선택", command=self.select_all_input)
        edit_menu.add_command(label="내용 지우기", command=self.clear_input)
        edit_menu.add_separator()
        edit_menu.add_command(label="결과 복사", command=self.copy_result)
        
        # 도구 메뉴
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도구", menu=tools_menu)
        tools_menu.add_command(label="API 상태 확인", command=self.check_api_status)
        tools_menu.add_command(label="설정", command=self.show_settings)
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용법", command=self.show_help)
        help_menu.add_command(label="프로그램 정보", command=self.show_about)
    
    def create_main_layout(self):
        """메인 레이아웃 생성"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 제목
        title_label = ttk.Label(main_frame, text="🤖 자동 글 변환 프로그램", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 왼쪽 컨트롤 패널
        self.create_control_panel(main_frame)
        
        # 오른쪽 메인 작업 영역
        self.create_work_area(main_frame)
    
    def create_control_panel(self, parent):
        """왼쪽 컨트롤 패널 생성"""
        control_frame = ttk.LabelFrame(parent, text="🔧 설정", padding="10")
        control_frame.grid(row=1, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 텍스트 입력 영역
        text_frame = ttk.LabelFrame(control_frame, text="� 텍스트 입력", padding="8")
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        text_frame.columnconfigure(0, weight=1)
        
        # 작은 텍스트 입력 칸
        self.control_text = tk.Text(text_frame, height=3, width=25, wrap=tk.WORD, font=('Arial', 9))
        self.control_text.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # 선택 옵션 영역
        option_frame = ttk.LabelFrame(control_frame, text="⚙️ 작업 선택", padding="8")
        option_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        option_frame.columnconfigure(0, weight=1)
        
        # 라디오 버튼 변수
        self.action_var = tk.StringVar(value="add")
        
        # 추가/삭제 선택 라디오 버튼
        ttk.Radiobutton(option_frame, text="➕ 추가", 
                       variable=self.action_var, value="add").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Radiobutton(option_frame, text="🗑️ 삭제", 
                       variable=self.action_var, value="delete").grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # 실행 버튼
        execute_btn = ttk.Button(option_frame, text="▶️ 실행", 
                               command=self.execute_action)
        execute_btn.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # API 상태
        api_frame = ttk.LabelFrame(control_frame, text="🔌 API 상태", padding="8")
        api_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        api_frame.columnconfigure(0, weight=1)
        
        self.api_status_label = ttk.Label(api_frame, text="❌ 연결되지 않음", foreground="red")
        self.api_status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 8))
        
        ttk.Button(api_frame, text="🔧 API 확인", 
                  command=self.check_api_status).grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 모델 선택
        model_frame = ttk.LabelFrame(control_frame, text="🤖 모델 선택", padding="8")
        model_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        model_frame.columnconfigure(0, weight=1)
        
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.model_var, 
                                       state="readonly", width=22)
        self.model_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        self.model_combo.bind('<<ComboboxSelected>>', self.on_model_selected)
        
        ttk.Button(model_frame, text="🔄 모델 변경", 
                  command=self.change_model).grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        control_frame.columnconfigure(0, weight=1)
    
    def create_work_area(self, parent):
        """오른쪽 작업 영역 생성"""
        work_frame = ttk.Frame(parent)
        work_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        work_frame.columnconfigure(0, weight=1)
        work_frame.rowconfigure(1, weight=1)
        work_frame.rowconfigure(3, weight=1)
        
        # 입력 영역
        input_frame = ttk.LabelFrame(work_frame, text="📝 변환할 텍스트 입력", padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, wrap=tk.WORD)
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 변환 버튼
        transform_btn = ttk.Button(work_frame, text="🚀 텍스트 변환하기", 
                                 command=self.transform_text, style='Accent.TButton')
        transform_btn.grid(row=2, column=0, pady=10)
        
        # 출력 영역
        output_frame = ttk.LabelFrame(work_frame, text="✨ 변환 결과", padding="10")
        output_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=8, wrap=tk.WORD, 
                                                   state=tk.DISABLED)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 결과 관리 버튼들
        result_btn_frame = ttk.Frame(work_frame)
        result_btn_frame.grid(row=4, column=0, pady=10)
        
        ttk.Button(result_btn_frame, text="💾 결과 저장", 
                  command=self.save_result).grid(row=0, column=0, padx=5)
        ttk.Button(result_btn_frame, text="📋 복사", 
                  command=self.copy_result).grid(row=0, column=1, padx=5)
        ttk.Button(result_btn_frame, text="🗑️ 지우기", 
                  command=self.clear_result).grid(row=0, column=2, padx=5)
    
    def create_status_bar(self):
        """상태바 생성"""
        self.status_bar = ttk.Label(self.root, text="프로그램을 시작합니다...", 
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def initialize_app(self):
        """앱 초기화"""
        self.update_status("제미나이 API 초기화 중...")
        
        # 기본 지침 초기화
        self._initialize_default_guidelines()
        
        # API 초기화를 별도 스레드에서 실행
        threading.Thread(target=self.initialize_api_async, daemon=True).start()
    
    def _initialize_default_guidelines(self):
        """기본 지침 초기화"""
        from prompt_system import DEFAULT_GUIDELINES
        existing_guidelines = self.prompt_system.list_guidelines()
        
        for name, guideline_data in DEFAULT_GUIDELINES.items():
            if name not in existing_guidelines:
                self.prompt_system.create_guideline(
                    name=guideline_data["name"],
                    description=guideline_data["description"],
                    rules=guideline_data["rules"],
                    examples=guideline_data["examples"]
                )
    
    def initialize_api_async(self):
        """API 비동기 초기화"""
        try:
            self.gemini_api = GeminiAPI(model_name=self.current_model)
            
            # 사용 가능한 모델 목록 로드
            self.load_available_models()
            
            if self.gemini_api.test_connection():
                self.root.after(0, lambda: self.update_api_status(True))
                self.root.after(0, lambda: self.update_status("준비 완료"))
            else:
                self.root.after(0, lambda: self.update_api_status(False))
                self.root.after(0, lambda: self.update_status("API 연결 실패"))
        except Exception as e:
            self.root.after(0, lambda: self.update_api_status(False))
            self.root.after(0, lambda: self.update_status(f"오류: {str(e)}"))
    
    def execute_action(self):
        """선택된 작업 실행"""
        action = self.action_var.get()
        text_content = self.control_text.get(1.0, tk.END).strip()
        
        if not text_content:
            messagebox.showwarning("경고", "텍스트를 입력해주세요.")
            return
        
        if action == "add":
            # 추가 작업 - 메인 입력창에 텍스트 추가
            current_content = self.input_text.get(1.0, tk.END).strip()
            if current_content:
                new_content = current_content + "\n\n" + text_content
            else:
                new_content = text_content
            
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, new_content)
            self.update_status(f"텍스트 추가됨: {len(text_content)}자")
            
        elif action == "delete":
            # 삭제 작업 - 메인 입력창에서 해당 텍스트 제거
            current_content = self.input_text.get(1.0, tk.END)
            if text_content in current_content:
                new_content = current_content.replace(text_content, "").strip()
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(tk.END, new_content)
                self.update_status(f"텍스트 삭제됨")
            else:
                messagebox.showinfo("정보", "삭제할 텍스트를 찾을 수 없습니다.")
        
        # 작업 완료 후 입력창 비우기
        self.control_text.delete(1.0, tk.END)
    
    def select_all_input(self):
        """입력창 전체 선택"""
        self.input_text.tag_add(tk.SEL, "1.0", tk.END)
        self.input_text.mark_set(tk.INSERT, "1.0")
        self.input_text.see(tk.INSERT)
    
    def clear_input(self):
        """입력창 내용 지우기"""
        if messagebox.askyesno("확인", "입력창의 모든 내용을 지우시겠습니까?"):
            self.input_text.delete(1.0, tk.END)
            self.update_status("입력창이 지워졌습니다")
    
    def update_api_status(self, connected):
        """API 상태 업데이트"""
        if connected:
            self.api_status_label.config(text="✅ 연결됨", foreground="green")
        else:
            self.api_status_label.config(text="❌ 연결되지 않음", foreground="red")
    
    def update_status(self, message):
        """상태바 메시지 업데이트"""
        self.status_bar.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
    
    def refresh_guidelines(self):
        """지침 목록 새로고침"""
        guidelines = self.prompt_system.list_guidelines()
        self.guideline_combo['values'] = guidelines
        
        # 지침 개수 업데이트
        self.guideline_count_label.config(text=f"📊 저장된 지침: {len(guidelines)}개")
        
        # 지침이 없는 경우
        if not guidelines:
            self.guideline_combo.set("")
            self.current_guideline = None
            self.update_guideline_status()
            return
        
        # 기존 지침이 여전히 존재하는 경우
        if self.current_guideline and self.current_guideline in guidelines:
            self.guideline_combo.set(self.current_guideline)
        # 기존 지침이 없거나 삭제된 경우
        elif guidelines:
            self.guideline_combo.set(guidelines[0])
            self.current_guideline = guidelines[0]
        else:
            self.guideline_combo.set("")
            self.current_guideline = None
            
        self.update_guideline_status()
    
    def update_guideline_status(self):
        """지침 상태 표시 업데이트"""
        if self.current_guideline:
            guideline_info = self.prompt_system.get_guideline(self.current_guideline)
            if guideline_info:
                status_text = f"✅ {guideline_info['name']}"
                self.guideline_status_label.config(text=status_text, foreground="green")
            else:
                self.guideline_status_label.config(text="❌ 지침 정보 오류", foreground="red")
        else:
            guidelines = self.prompt_system.list_guidelines()
            if not guidelines:
                self.guideline_status_label.config(text="⚠️ 지침이 없습니다. 새 지침을 만들어주세요", foreground="orange")
            else:
                self.guideline_status_label.config(text="❌ 지침을 선택해주세요", foreground="red")
    
    def on_guidelines_changed(self):
        """지침이 변경되었을 때 호출되는 콜백"""
        self.refresh_guidelines()
        self.update_status("지침 목록이 업데이트되었습니다")
    
    def load_available_models(self):
        """사용 가능한 모델 목록 로드"""
        if self.gemini_api:
            try:
                models = self.gemini_api.get_available_models()
                # 주요 모델들을 우선순위로 정렬
                priority_models = [
                    'gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash-exp',
                    'gemini-2.0-flash', 'gemini-flash-latest', 'gemini-pro-latest'
                ]
                
                sorted_models = []
                for model in priority_models:
                    if model in models:
                        sorted_models.append(model)
                
                # 나머지 모델들 추가
                for model in models:
                    if model not in sorted_models:
                        sorted_models.append(model)
                
                self.root.after(0, lambda: self._update_model_combo(sorted_models))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"모델 목록 로드 실패: {str(e)}"))
    
    def _update_model_combo(self, models):
        """모델 콤보박스 업데이트 (메인 스레드에서 실행)"""
        self.model_combo['values'] = models
        if self.current_model in models:
            self.model_combo.set(self.current_model)
        elif models:
            self.model_combo.set(models[0])
    
    def on_model_selected(self, event=None):
        """모델 선택 이벤트"""
        selected = self.model_var.get()
        if selected and selected != self.current_model:
            self.update_status(f"모델 선택됨: {selected} (변경하려면 '🔄 모델 변경' 버튼 클릭)")
    
    def change_model(self):
        """선택된 모델로 변경"""
        if not self.gemini_api:
            messagebox.showerror("오류", "API가 초기화되지 않았습니다.")
            return
        
        selected_model = self.model_var.get()
        if not selected_model:
            messagebox.showwarning("경고", "변경할 모델을 선택해주세요.")
            return
        
        if selected_model == self.current_model:
            messagebox.showinfo("정보", "현재 사용 중인 모델과 동일합니다.")
            return
        
        # 확인 대화상자
        if messagebox.askyesno("모델 변경", 
                              f"모델을 '{selected_model}'로 변경하시겠습니까?\n\n"
                              f"현재: {self.current_model}\n"
                              f"변경: {selected_model}"):
            
            self.update_status("모델 변경 중...")
            threading.Thread(target=self.change_model_async, args=(selected_model,), daemon=True).start()
    
    def change_model_async(self, new_model):
        """모델 비동기 변경"""
        try:
            success = self.gemini_api.change_model(new_model)
            
            if success:
                self.current_model = new_model
                self.root.after(0, lambda: self.update_status(f"모델 변경 완료: {new_model}"))
                self.root.after(0, lambda: messagebox.showinfo("완료", f"모델이 '{new_model}'로 변경되었습니다."))
                
                # API 연결 재테스트
                if self.gemini_api.test_connection():
                    self.root.after(0, lambda: self.update_api_status(True))
                else:
                    self.root.after(0, lambda: self.update_api_status(False))
                    
            else:
                self.root.after(0, lambda: messagebox.showerror("오류", "모델 변경에 실패했습니다."))
                self.root.after(0, lambda: self.update_status("모델 변경 실패"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("오류", f"모델 변경 중 오류: {str(e)}"))
            self.root.after(0, lambda: self.update_status("모델 변경 실패"))
    
    def on_guideline_selected(self, event=None):
        """지침 선택 이벤트"""
        selected = self.guideline_var.get()
        if selected:
            self.current_guideline = selected
            guideline_info = self.prompt_system.get_guideline(selected)
            if guideline_info:
                self.update_status(f"지침 설정: {guideline_info['name']}")
                self.update_guideline_status()
            else:
                self.update_status("지침 정보를 불러올 수 없습니다")
        else:
            self.current_guideline = None
            self.update_guideline_status()
    
    def transform_text(self):
        """텍스트 변환 실행"""
        if not self.gemini_api:
            messagebox.showerror("오류", "API가 초기화되지 않았습니다.")
            return
        
        input_text = self.input_text.get(1.0, tk.END).strip()
        if not input_text:
            messagebox.showwarning("경고", "변환할 텍스트를 입력해주세요.")
            return
        
        self.update_status("텍스트 변환 중...")
        
        # 기본 지침 사용
        default_guideline = "유사문서회피_HTML생성"
        
        # 변환을 별도 스레드에서 실행
        threading.Thread(target=self.transform_text_async, args=(input_text, default_guideline), daemon=True).start()
    
    def transform_text_async(self, input_text, guideline_name):
        """텍스트 변환 비동기 실행"""
        try:
            prompt = self.prompt_system.build_prompt(guideline_name, input_text)
            
            if prompt.startswith("오류:"):
                self.root.after(0, lambda: messagebox.showerror("오류", prompt))
                return
            
            result = self.gemini_api.generate_text(prompt)
            
            # UI 업데이트는 메인 스레드에서
            self.root.after(0, lambda: self.display_result(result))
            self.root.after(0, lambda: self.update_status("변환 완료"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("오류", f"변환 중 오류 발생: {str(e)}"))
            self.root.after(0, lambda: self.update_status("변환 실패"))
    
    def display_result(self, result):
        """결과 표시"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, result)
        self.output_text.config(state=tk.DISABLED)
    
    def copy_result(self):
        """결과 클립보드에 복사"""
        result = self.output_text.get(1.0, tk.END).strip()
        if result:
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.update_status("결과를 클립보드에 복사했습니다")
        else:
            messagebox.showwarning("경고", "복사할 결과가 없습니다.")
    
    def clear_result(self):
        """결과 지우기"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.update_status("결과를 지웠습니다")
    
    def save_result(self):
        """결과 파일로 저장"""
        result = self.output_text.get(1.0, tk.END).strip()
        if not result:
            messagebox.showwarning("경고", "저장할 결과가 없습니다.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    input_text = self.input_text.get(1.0, tk.END).strip()
                    f.write(f"원본 텍스트:\n{input_text}\n\n")
                    f.write(f"변환 결과 (지침: {self.current_guideline}):\n{result}")
                
                messagebox.showinfo("완료", f"결과가 저장되었습니다:\n{filename}")
                self.update_status(f"결과 저장 완료: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("오류", f"저장 실패: {str(e)}")
    
    def load_result(self):
        """결과 파일 불러오기"""
        filename = filedialog.askopenfilename(
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.output_text.config(state=tk.NORMAL)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, content)
                self.output_text.config(state=tk.DISABLED)
                
                self.update_status(f"파일 불러오기 완료: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("오류", f"불러오기 실패: {str(e)}")
    
    def create_new_guideline(self):
        """새 지침 생성 대화상자"""
        GuidelineDialog(self.root, self.prompt_system, callback=self.on_guidelines_changed)
    
    def edit_guideline(self):
        """지침 수정"""
        if not self.current_guideline:
            messagebox.showwarning("경고", "수정할 지침을 선택해주세요.")
            return
        
        GuidelineDialog(self.root, self.prompt_system, 
                       edit_guideline=self.current_guideline, 
                       callback=self.on_guidelines_changed)
    
    def delete_guideline(self):
        """지침 삭제"""
        if not self.current_guideline:
            messagebox.showwarning("경고", "삭제할 지침을 선택해주세요.")
            return
        
        if messagebox.askyesno("확인", f"'{self.current_guideline}' 지침을 정말 삭제하시겠습니까?"):
            if self.prompt_system.delete_guideline(self.current_guideline):
                messagebox.showinfo("완료", "지침이 삭제되었습니다.")
                self.current_guideline = None
                self.on_guidelines_changed()
            else:
                messagebox.showerror("오류", "지침 삭제에 실패했습니다.")
    
    def show_guidelines_window(self):
        """지침 목록 창 표시"""
        GuidelineListWindow(self.root, self.prompt_system)
    
    def check_api_status(self):
        """API 상태 확인"""
        if not self.gemini_api:
            messagebox.showwarning("경고", "API가 초기화되지 않았습니다.")
            return
        
        self.update_status("API 상태 확인 중...")
        threading.Thread(target=self.check_api_status_async, daemon=True).start()
    
    def check_api_status_async(self):
        """API 상태 비동기 확인"""
        try:
            is_connected = self.gemini_api.test_connection()
            info = self.gemini_api.get_model_info()
            
            status_msg = "✅ 연결됨" if is_connected else "❌ 연결 실패"
            detailed_info = f"""
API 상태: {status_msg}
현재 모델: {info['model_name']}
API 키 설정: {'✅' if info['api_key_set'] else '❌'}
Temperature: {info['generation_config']['temperature']}
Max tokens: {info['generation_config']['max_output_tokens']}

💡 모델 변경은 왼쪽 패널의 '모델 선택'에서 가능합니다.
            """.strip()
            
            self.root.after(0, lambda: messagebox.showinfo("API 상태", detailed_info))
            self.root.after(0, lambda: self.update_api_status(is_connected))
            self.root.after(0, lambda: self.update_status("API 상태 확인 완료"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("오류", f"API 상태 확인 실패: {str(e)}"))
    
    def show_settings(self):
        """설정 창 표시"""
        messagebox.showinfo("설정", "설정 기능은 추후 업데이트 예정입니다.")
    
    def show_help(self):
        """도움말 표시"""
        help_text = """
🤖 자동 글 변환 프로그램 사용법

1. 지침 설정:
   - 왼쪽 패널에서 지침을 선택하세요
   - 새 지침을 만들려면 "➕ 새 지침" 버튼을 클릭하세요

2. 텍스트 변환:
   - 상단 입력창에 변환할 텍스트를 입력하세요
   - "🚀 텍스트 변환하기" 버튼을 클릭하세요
   - 하단에 변환된 결과가 표시됩니다

3. 결과 관리:
   - 💾 결과 저장: 텍스트 파일로 저장
   - 📋 복사: 클립보드에 복사
   - 🗑️ 지우기: 결과 내용 삭제

4. 지침 관리:
   - ➕ 새 지침: 새로운 변환 규칙 생성
   - ✏️ 수정: 기존 지침 내용 변경
   - 🗑️ 삭제: 지침 삭제
   - 📋 목록: 모든 지침 목록 보기

팁: API 연결 상태를 확인하고 지침을 설정한 후 사용하세요!
        """.strip()
        
        messagebox.showinfo("사용법", help_text)
    
    def show_about(self):
        """프로그램 정보 표시"""
        about_text = """
🤖 자동 글 변환 프로그램 v1.0

제미나이 API를 활용한 지침 기반 텍스트 변환 도구

✨ 주요 기능:
- 사용자 정의 지침에 따른 텍스트 변환
- 직관적인 GUI 인터페이스
- 결과 저장 및 관리
- 지침 생성 및 수정

🔧 기술 스택:
- Python 3.x
- tkinter (GUI)
- Google Gemini API
- JSON (데이터 저장)

© 2025 자동 글 변환 프로그램
        """.strip()
        
        messagebox.showinfo("프로그램 정보", about_text)
    
    def run(self):
        """GUI 애플리케이션 실행"""
        self.root.mainloop()


class GuidelineDialog:
    """지침 생성/수정 대화상자"""
    def __init__(self, parent, prompt_system, edit_guideline=None, callback=None):
        self.prompt_system = prompt_system
        self.callback = callback
        self.edit_mode = edit_guideline is not None
        
        # 대화상자 생성
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("지침 수정" if self.edit_mode else "새 지침 만들기")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 기존 지침 정보 불러오기 (수정 모드인 경우)
        self.original_guideline = None
        if self.edit_mode:
            self.original_guideline = self.prompt_system.get_guideline(edit_guideline)
        
        self.create_dialog_layout()
        
        # 수정 모드인 경우 기존 정보 채우기
        if self.edit_mode and self.original_guideline:
            self.load_existing_data()
    
    def create_dialog_layout(self):
        """대화상자 레이아웃 생성"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        row = 0
        
        # 지침 이름
        ttk.Label(main_frame, text="지침 이름:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=50)
        name_entry.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        row += 1
        
        # 지침 설명
        ttk.Label(main_frame, text="지침 설명:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        self.description_text = scrolledtext.ScrolledText(main_frame, height=4, width=50)
        self.description_text.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        row += 1
        
        # 규칙들
        ttk.Label(main_frame, text="규칙들:", font=('Arial', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        self.rules_text = scrolledtext.ScrolledText(main_frame, height=8, width=50)
        self.rules_text.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        row += 1
        
        ttk.Label(main_frame, text="(한 줄에 하나씩 입력하세요)", 
                 font=('Arial', 8), foreground='gray').grid(row=row, column=0, sticky=tk.W, pady=(0, 15))
        row += 1
        
        # 버튼들
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, pady=20)
        
        ttk.Button(btn_frame, text="취소", 
                  command=self.dialog.destroy).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="수정" if self.edit_mode else "생성", 
                  command=self.save_guideline).grid(row=0, column=1, padx=10)
    
    def load_existing_data(self):
        """기존 지침 데이터 로드 (수정 모드)"""
        if not self.original_guideline:
            return
        
        self.name_var.set(self.original_guideline['name'])
        
        self.description_text.insert(tk.END, self.original_guideline['description'])
        
        rules_text = '\n'.join(self.original_guideline['rules'])
        self.rules_text.insert(tk.END, rules_text)
    
    def save_guideline(self):
        """지침 저장"""
        # 입력 검증
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("오류", "지침 이름을 입력해주세요.")
            return
        
        description = self.description_text.get(1.0, tk.END).strip()
        if not description:
            messagebox.showerror("오류", "지침 설명을 입력해주세요.")
            return
        
        rules_text = self.rules_text.get(1.0, tk.END).strip()
        if not rules_text:
            messagebox.showerror("오류", "최소 하나의 규칙을 입력해주세요.")
            return
        
        rules = [rule.strip() for rule in rules_text.split('\n') if rule.strip()]
        
        # 지침 저장
        if self.edit_mode:
            # 수정 모드
            success = self.prompt_system.update_guideline(
                self.original_guideline['name'],
                description=description,
                rules=rules
            )
        else:
            # 생성 모드
            # 중복 이름 확인
            existing_guidelines = self.prompt_system.list_guidelines()
            if name in existing_guidelines:
                messagebox.showerror("오류", "이미 존재하는 지침 이름입니다.")
                return
            
            success = self.prompt_system.create_guideline(name, description, rules)
        
        if success:
            messagebox.showinfo("완료", "지침이 저장되었습니다.")
            if self.callback:
                self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("오류", "지침 저장에 실패했습니다.")


class GuidelineListWindow:
    """지침 목록 창"""
    def __init__(self, parent, prompt_system):
        self.prompt_system = prompt_system
        
        # 창 생성
        self.window = tk.Toplevel(parent)
        self.window.title("📋 지침 목록")
        self.window.geometry("700x500")
        self.window.transient(parent)
        
        self.create_layout()
        self.refresh_list()
    
    def create_layout(self):
        """레이아웃 생성"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 제목
        ttk.Label(main_frame, text="📋 저장된 지침 목록", 
                 style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # 목록 프레임
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 트리뷰 (목록)
        columns = ('이름', '설명', '규칙수', '생성일')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 컬럼 설정
        self.tree.heading('이름', text='지침 이름')
        self.tree.heading('설명', text='설명')
        self.tree.heading('규칙수', text='규칙 수')
        self.tree.heading('생성일', text='생성일')
        
        self.tree.column('이름', width=150)
        self.tree.column('설명', width=300)
        self.tree.column('규칙수', width=80)
        self.tree.column('생성일', width=120)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 더블클릭 이벤트
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
        # 버튼 프레임
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, pady=20)
        
        ttk.Button(btn_frame, text="🔄 새로고침", 
                  command=self.refresh_list).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="📖 상세보기", 
                  command=self.show_details).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="닫기", 
                  command=self.window.destroy).grid(row=0, column=2, padx=5)
    
    def refresh_list(self):
        """목록 새로고침"""
        # 기존 아이템 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 지침 목록 불러오기
        guidelines = self.prompt_system.list_guidelines()
        
        for name in guidelines:
            guideline = self.prompt_system.get_guideline(name)
            
            # 생성일 포맷팅
            created_at = guideline.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_at = dt.strftime('%Y-%m-%d')
                except:
                    created_at = created_at[:10] if len(created_at) >= 10 else created_at
            
            self.tree.insert('', tk.END, values=(
                guideline['name'],
                guideline['description'][:50] + '...' if len(guideline['description']) > 50 else guideline['description'],
                len(guideline['rules']),
                created_at
            ))
    
    def on_item_double_click(self, event):
        """아이템 더블클릭 이벤트"""
        self.show_details()
    
    def show_details(self):
        """선택된 지침 상세보기"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("경고", "지침을 선택해주세요.")
            return
        
        item = self.tree.item(selection[0])
        guideline_name = item['values'][0]
        
        GuidelineDetailWindow(self.window, self.prompt_system, guideline_name)


class GuidelineDetailWindow:
    """지침 상세보기 창"""
    def __init__(self, parent, prompt_system, guideline_name):
        self.prompt_system = prompt_system
        self.guideline_name = guideline_name
        
        # 창 생성
        self.window = tk.Toplevel(parent)
        self.window.title(f"📖 {guideline_name} - 상세정보")
        self.window.geometry("600x500")
        self.window.transient(parent)
        
        self.create_layout()
        self.load_guideline_data()
    
    def create_layout(self):
        """레이아웃 생성"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 제목
        self.title_label = ttk.Label(main_frame, style='Title.TLabel')
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        
        # 스크롤 가능한 텍스트 영역
        self.detail_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                   state=tk.DISABLED, height=20)
        self.detail_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # 닫기 버튼
        ttk.Button(main_frame, text="닫기", 
                  command=self.window.destroy).grid(row=2, column=0)
    
    def load_guideline_data(self):
        """지침 데이터 로드 및 표시"""
        guideline = self.prompt_system.get_guideline(self.guideline_name)
        
        if not guideline:
            messagebox.showerror("오류", "지침 정보를 불러올 수 없습니다.")
            self.window.destroy()
            return
        
        # 제목 설정
        self.title_label.config(text=f"📖 {guideline['name']}")
        
        # 상세 정보 생성
        detail_content = f"""📋 지침 이름: {guideline['name']}

📝 설명:
{guideline['description']}

📌 규칙들:
"""
        
        for i, rule in enumerate(guideline['rules'], 1):
            detail_content += f"{i}. {rule}\n"
        
        # 예시가 있다면 추가
        if guideline.get('examples'):
            detail_content += "\n💡 예시들:\n"
            for i, example in enumerate(guideline['examples'], 1):
                detail_content += f"\n예시 {i}:\n"
                detail_content += f"  입력: {example.get('input', '')}\n"
                detail_content += f"  출력: {example.get('output', '')}\n"
        
        # 메타 정보
        detail_content += f"""

📅 생성일: {guideline.get('created_at', 'Unknown')}
📅 수정일: {guideline.get('updated_at', 'Unknown')}
"""
        
        # 텍스트 표시
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(tk.END, detail_content)
        self.detail_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    app = TextTransformGUI()
    app.run()