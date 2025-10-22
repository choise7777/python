"""
GUI 프로그램 실행 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from gui_main import TextTransformGUI
    
    print("🚀 GUI 프로그램을 시작합니다...")
    app = TextTransformGUI()
    app.run()
    
except ImportError as e:
    print(f"❌ 모듈 불러오기 실패: {e}")
    print("필요한 패키지가 설치되었는지 확인해주세요.")
    
except Exception as e:
    print(f"❌ 프로그램 실행 중 오류: {e}")
    
finally:
    print("👋 프로그램이 종료되었습니다.")