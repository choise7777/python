"""
자동 글 변환 프로그램 - 사용 예시 데모
"""

from gemini_api import GeminiAPI
from prompt_system import PromptSystem

def demo():
    print("🚀 자동 글 변환 프로그램 데모")
    print("="*50)
    
    # API 초기화
    print("1️⃣ API 초기화 중...")
    api = GeminiAPI()
    
    # 프롬프트 시스템 초기화
    print("2️⃣ 프롬프트 시스템 초기화 중...")
    prompt_system = PromptSystem()
    
    # 기본 지침들 확인
    print("3️⃣ 사용 가능한 지침들:")
    guidelines = prompt_system.list_guidelines()
    for i, guideline in enumerate(guidelines, 1):
        info = prompt_system.get_guideline(guideline)
        print(f"   {i}. {info['name']} - {info['description']}")
    
    print("\n4️⃣ 실제 변환 예시:")
    
    # 예시 1: 정식 문서 작성
    print("\n📝 예시 1: 정식 문서 작성")
    print("-" * 30)
    user_text = "내일 회의 취소하고 싶어"
    prompt = prompt_system.build_prompt("정식 문서 작성", user_text)
    
    print(f"입력: {user_text}")
    print("변환 중...")
    result = api.generate_text(prompt)
    print(f"결과: {result}")
    
    # 예시 2: 친근한 대화체
    print("\n💬 예시 2: 친근한 대화체")
    print("-" * 30)
    user_text = "새로운 프로젝트를 시작했습니다"
    prompt = prompt_system.build_prompt("친근한 대화체", user_text)
    
    print(f"입력: {user_text}")
    print("변환 중...")
    result = api.generate_text(prompt)
    print(f"결과: {result}")
    
    print("\n✨ 데모 완료! 메인 프로그램을 실행하여 더 많은 기능을 사용해보세요.")
    print("실행 명령: python main.py")

if __name__ == "__main__":
    demo()