"""
GUI 기능 테스트 스크립트
GUI 프로그램의 각 기능이 정상 동작하는지 확인
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """필요한 모듈들이 정상적으로 임포트되는지 테스트"""
    print("📋 모듈 임포트 테스트...")
    
    try:
        from gemini_api import GeminiAPI
        print("✅ gemini_api 모듈 임포트 성공")
        
        from prompt_system import PromptSystem
        print("✅ prompt_system 모듈 임포트 성공")
        
        from gui_main import TextTransformGUI
        print("✅ gui_main 모듈 임포트 성공")
        
        return True
    except ImportError as e:
        print(f"❌ 모듈 임포트 실패: {e}")
        return False

def test_gui_creation():
    """GUI 창 생성 테스트"""
    print("\n🖥️ GUI 창 생성 테스트...")
    
    try:
        # 임시 루트 창 생성
        root = tk.Tk()
        root.withdraw()  # 숨김
        
        # 기본 tkinter 위젯들 테스트
        test_window = tk.Toplevel(root)
        test_window.title("GUI 테스트")
        test_window.geometry("300x200")
        
        # 기본 위젯들
        tk.Label(test_window, text="GUI 테스트 창").pack(pady=10)
        tk.Button(test_window, text="테스트 완료", 
                 command=test_window.destroy).pack(pady=10)
        
        print("✅ 기본 GUI 위젯 생성 성공")
        
        # 잠시 표시 후 자동 닫기
        test_window.after(2000, test_window.destroy)
        test_window.after(2100, root.destroy)
        
        root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI 생성 실패: {e}")
        return False

def test_backend_connection():
    """백엔드 연결 테스트"""
    print("\n🔌 백엔드 연결 테스트...")
    
    try:
        from gemini_api import GeminiAPI
        from prompt_system import PromptSystem
        
        # 프롬프트 시스템 테스트
        prompt_system = PromptSystem()
        guidelines = prompt_system.list_guidelines()
        print(f"✅ 지침 시스템 연결 성공 (지침 수: {len(guidelines)}개)")
        
        # API 테스트 (연결만 확인, 실제 호출은 하지 않음)
        try:
            api = GeminiAPI()
            print("✅ 제미나이 API 초기화 성공")
        except Exception as api_error:
            print(f"⚠️ API 초기화 실패: {api_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ 백엔드 연결 실패: {e}")
        return False

def run_gui_test():
    """실제 GUI 프로그램 테스트 실행"""
    print("\n🚀 GUI 프로그램 실행 테스트...")
    
    try:
        from gui_main import TextTransformGUI
        
        print("GUI 프로그램을 시작합니다...")
        print("(테스트를 위해 5초 후 자동으로 종료됩니다)")
        
        app = TextTransformGUI()
        
        # 5초 후 자동 종료
        def auto_close():
            print("✅ GUI 테스트 완료 - 프로그램을 종료합니다")
            app.root.destroy()
        
        app.root.after(5000, auto_close)
        app.run()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI 실행 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 GUI 프로그램 기능 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("모듈 임포트", test_imports),
        ("GUI 창 생성", test_gui_creation),
        ("백엔드 연결", test_backend_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트 통과! GUI 프로그램이 정상적으로 작동할 수 있습니다.")
        
        # 사용자에게 실제 GUI 실행 여부 묻기
        response = input("\n실제 GUI 프로그램을 실행하시겠습니까? (y/n): ").lower()
        if response == 'y':
            run_gui_test()
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 문제를 해결한 후 다시 시도해주세요.")

if __name__ == "__main__":
    main()