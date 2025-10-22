"""
간단한 API 연결 테스트
"""

from gemini_api import GeminiAPI

def test_api():
    try:
        print("🔄 제미나이 API 연결 테스트 중...")
        api = GeminiAPI()
        
        if api.test_connection():
            print("✅ API 연결 성공!")
            return True
        else:
            print("❌ API 연결 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    test_api()