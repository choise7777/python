"""
사용 가능한 제미나이 모델 목록 확인
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

def list_models():
    try:
        # .env 파일 로드
        load_dotenv()
        
        # API 키 설정
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ API 키가 설정되지 않았습니다.")
            return
        
        genai.configure(api_key=api_key)
        
        print("🔍 사용 가능한 모델 목록:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    list_models()