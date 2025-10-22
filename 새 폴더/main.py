"""
자동 글 변환 프로그램 - 메인 프로그램
제미나이 API를 활용한 지침 기반 텍스트 변환 시스템
"""

import os
import sys
from typing import Optional
from gemini_api import GeminiAPI
from prompt_system import PromptSystem, DEFAULT_GUIDELINES

class TextTransformationApp:
    def __init__(self):
        """애플리케이션 초기화"""
        self.gemini_api = None
        self.prompt_system = PromptSystem()
        self.current_guideline = None
        
        # 기본 지침이 없으면 추가
        self._initialize_default_guidelines()
    
    def _initialize_default_guidelines(self):
        """기본 지침 초기화"""
        existing_guidelines = self.prompt_system.list_guidelines()
        
        for name, guideline_data in DEFAULT_GUIDELINES.items():
            if name not in existing_guidelines:
                self.prompt_system.create_guideline(
                    name=guideline_data["name"],
                    description=guideline_data["description"],
                    rules=guideline_data["rules"],
                    examples=guideline_data["examples"]
                )
    
    def initialize_api(self) -> bool:
        """API 초기화 및 연결 테스트"""
        try:
            print("🔄 제미나이 API 연결을 확인하고 있습니다...")
            self.gemini_api = GeminiAPI()
            
            if self.gemini_api.test_connection():
                print("✅ 제미나이 API 연결 성공!")
                return True
            else:
                print("❌ API 연결에 실패했습니다.")
                return False
                
        except Exception as e:
            print(f"❌ API 초기화 실패: {str(e)}")
            return False
    
    def display_menu(self):
        """메인 메뉴 표시"""
        print("\n" + "="*50)
        print("🤖 자동 글 변환 프로그램")
        print("="*50)
        print("1. 📝 텍스트 변환 (지침 적용)")
        print("2. 📋 지침 관리")
        print("3. 📊 지침 목록 보기")
        print("4. ⚙️  현재 지침 설정")
        print("5. 🔧 API 상태 확인")
        print("0. 🚪 프로그램 종료")
        print("-"*50)
    
    def display_guideline_menu(self):
        """지침 관리 메뉴 표시"""
        print("\n" + "="*40)
        print("📋 지침 관리")
        print("="*40)
        print("1. ➕ 새 지침 생성")
        print("2. ✏️  기존 지침 수정")
        print("3. 🗑️  지침 삭제")
        print("4. 📖 지침 상세보기")
        print("0. 🔙 메인 메뉴로")
        print("-"*40)
    
    def transform_text(self):
        """텍스트 변환 실행"""
        if not self.gemini_api:
            print("❌ API가 초기화되지 않았습니다.")
            return
        
        if not self.current_guideline:
            print("❌ 현재 설정된 지침이 없습니다.")
            print("   먼저 지침을 설정해주세요. (메뉴 4번)")
            return
        
        print(f"\n📝 텍스트 변환 (현재 지침: {self.current_guideline})")
        print("-"*50)
        
        # 사용자 입력 받기
        print("변환할 텍스트를 입력하세요 (여러 줄 입력 시 빈 줄로 끝내세요):")
        lines = []
        while True:
            line = input()
            if line.strip() == "" and lines:
                break
            lines.append(line)
        
        user_input = "\n".join(lines)
        if not user_input.strip():
            print("❌ 입력된 텍스트가 없습니다.")
            return
        
        # 프롬프트 구성 및 변환 실행
        print("\n🔄 텍스트 변환 중...")
        prompt = self.prompt_system.build_prompt(self.current_guideline, user_input)
        
        if prompt.startswith("오류:"):
            print(f"❌ {prompt}")
            return
        
        # API 호출
        result = self.gemini_api.generate_text(prompt)
        
        # 결과 출력
        print("\n" + "="*50)
        print("✨ 변환 결과:")
        print("="*50)
        print(result)
        print("="*50)
        
        # 결과 저장 옵션
        save = input("\n💾 결과를 파일로 저장하시겠습니까? (y/N): ").lower()
        if save == 'y':
            filename = input("파일명을 입력하세요 (확장자 제외): ")
            if filename:
                try:
                    filepath = f"{filename}.txt"
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"원본:\n{user_input}\n\n")
                        f.write(f"변환 결과 (지침: {self.current_guideline}):\n{result}")
                    print(f"✅ 결과가 '{filepath}' 파일로 저장되었습니다.")
                except Exception as e:
                    print(f"❌ 파일 저장 실패: {str(e)}")
    
    def manage_guidelines(self):
        """지침 관리"""
        while True:
            self.display_guideline_menu()
            choice = input("선택하세요: ").strip()
            
            if choice == '1':
                self._create_new_guideline()
            elif choice == '2':
                self._edit_guideline()
            elif choice == '3':
                self._delete_guideline()
            elif choice == '4':
                self._view_guideline_details()
            elif choice == '0':
                break
            else:
                print("❌ 올바른 선택이 아닙니다.")
    
    def _create_new_guideline(self):
        """새 지침 생성"""
        print("\n➕ 새 지침 생성")
        print("-"*30)
        
        name = input("지침 이름: ").strip()
        if not name:
            print("❌ 지침 이름은 필수입니다.")
            return
        
        if name in self.prompt_system.list_guidelines():
            print("❌ 이미 존재하는 지침 이름입니다.")
            return
        
        description = input("지침 설명: ").strip()
        if not description:
            print("❌ 지침 설명은 필수입니다.")
            return
        
        print("규칙들을 입력하세요 (빈 줄로 끝내세요):")
        rules = []
        while True:
            rule = input(f"규칙 {len(rules)+1}: ").strip()
            if not rule:
                break
            rules.append(rule)
        
        if not rules:
            print("❌ 최소 하나의 규칙은 필요합니다.")
            return
        
        # 예시 추가 (선택사항)
        examples = []
        add_example = input("예시를 추가하시겠습니까? (y/N): ").lower()
        
        while add_example == 'y':
            example_input = input("예시 입력: ").strip()
            example_output = input("예시 출력: ").strip()
            
            if example_input and example_output:
                examples.append({"input": example_input, "output": example_output})
                add_example = input("또 다른 예시를 추가하시겠습니까? (y/N): ").lower()
            else:
                print("❌ 입력과 출력 모두 필요합니다.")
                break
        
        # 지침 생성
        if self.prompt_system.create_guideline(name, description, rules, examples):
            print(f"✅ '{name}' 지침이 생성되었습니다.")
        else:
            print("❌ 지침 생성에 실패했습니다.")
    
    def _edit_guideline(self):
        """기존 지침 수정"""
        guidelines = self.prompt_system.list_guidelines()
        if not guidelines:
            print("❌ 수정할 지침이 없습니다.")
            return
        
        print("\n✏️ 기존 지침 수정")
        print("수정 가능한 지침:")
        for i, name in enumerate(guidelines, 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input("수정할 지침 번호: ")) - 1
            if 0 <= choice < len(guidelines):
                guideline_name = guidelines[choice]
                guideline = self.prompt_system.get_guideline(guideline_name)
                
                print(f"\n현재 지침 정보:")
                print(f"이름: {guideline['name']}")
                print(f"설명: {guideline['description']}")
                print(f"규칙 수: {len(guideline['rules'])}개")
                
                # 수정할 항목 선택
                print("\n수정할 항목을 선택하세요:")
                print("1. 설명")
                print("2. 규칙")
                print("0. 취소")
                
                edit_choice = input("선택: ").strip()
                
                if edit_choice == '1':
                    new_description = input(f"새 설명 (현재: {guideline['description']}): ").strip()
                    if new_description:
                        self.prompt_system.update_guideline(guideline_name, description=new_description)
                        print("✅ 설명이 업데이트되었습니다.")
                
                elif edit_choice == '2':
                    print("새 규칙들을 입력하세요 (빈 줄로 끝내세요):")
                    new_rules = []
                    while True:
                        rule = input(f"규칙 {len(new_rules)+1}: ").strip()
                        if not rule:
                            break
                        new_rules.append(rule)
                    
                    if new_rules:
                        self.prompt_system.update_guideline(guideline_name, rules=new_rules)
                        print("✅ 규칙이 업데이트되었습니다.")
            else:
                print("❌ 올바른 번호를 선택하세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _delete_guideline(self):
        """지침 삭제"""
        guidelines = self.prompt_system.list_guidelines()
        if not guidelines:
            print("❌ 삭제할 지침이 없습니다.")
            return
        
        print("\n🗑️ 지침 삭제")
        print("삭제 가능한 지침:")
        for i, name in enumerate(guidelines, 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input("삭제할 지침 번호: ")) - 1
            if 0 <= choice < len(guidelines):
                guideline_name = guidelines[choice]
                
                confirm = input(f"정말로 '{guideline_name}' 지침을 삭제하시겠습니까? (y/N): ").lower()
                if confirm == 'y':
                    if self.prompt_system.delete_guideline(guideline_name):
                        print(f"✅ '{guideline_name}' 지침이 삭제되었습니다.")
                        
                        # 현재 지침이 삭제된 경우 해제
                        if self.current_guideline == guideline_name:
                            self.current_guideline = None
                            print("⚠️ 현재 설정된 지침이 삭제되어 지침 설정이 해제되었습니다.")
                    else:
                        print("❌ 지침 삭제에 실패했습니다.")
            else:
                print("❌ 올바른 번호를 선택하세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def _view_guideline_details(self):
        """지침 상세보기"""
        guidelines = self.prompt_system.list_guidelines()
        if not guidelines:
            print("❌ 조회할 지침이 없습니다.")
            return
        
        print("\n📖 지침 상세보기")
        print("조회할 지침:")
        for i, name in enumerate(guidelines, 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input("조회할 지침 번호: ")) - 1
            if 0 <= choice < len(guidelines):
                guideline_name = guidelines[choice]
                guideline = self.prompt_system.get_guideline(guideline_name)
                
                print(f"\n{'='*40}")
                print(f"📋 {guideline['name']}")
                print('='*40)
                print(f"설명: {guideline['description']}")
                print(f"\n📌 규칙들:")
                for i, rule in enumerate(guideline['rules'], 1):
                    print(f"  {i}. {rule}")
                
                if guideline['examples']:
                    print(f"\n💡 예시들:")
                    for i, example in enumerate(guideline['examples'], 1):
                        print(f"  예시 {i}:")
                        print(f"    입력: {example['input']}")
                        print(f"    출력: {example['output']}")
                
                print(f"\n📅 생성일: {guideline.get('created_at', 'Unknown')}")
                print(f"📅 수정일: {guideline.get('updated_at', 'Unknown')}")
                print('='*40)
            else:
                print("❌ 올바른 번호를 선택하세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def show_guidelines_list(self):
        """지침 목록 보기"""
        summary = self.prompt_system.get_guidelines_summary()
        print(f"\n{summary}")
    
    def set_current_guideline(self):
        """현재 사용할 지침 설정"""
        guidelines = self.prompt_system.list_guidelines()
        if not guidelines:
            print("❌ 설정할 지침이 없습니다.")
            return
        
        print(f"\n⚙️ 현재 지침 설정 (현재: {self.current_guideline or '없음'})")
        print("사용할 지침을 선택하세요:")
        for i, name in enumerate(guidelines, 1):
            marker = " ← 현재" if name == self.current_guideline else ""
            print(f"{i}. {name}{marker}")
        print("0. 지침 해제")
        
        try:
            choice = int(input("선택: "))
            if choice == 0:
                self.current_guideline = None
                print("✅ 지침이 해제되었습니다.")
            elif 1 <= choice <= len(guidelines):
                self.current_guideline = guidelines[choice - 1]
                print(f"✅ '{self.current_guideline}' 지침이 설정되었습니다.")
            else:
                print("❌ 올바른 번호를 선택하세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")
    
    def check_api_status(self):
        """API 상태 확인"""
        if not self.gemini_api:
            print("❌ API가 초기화되지 않았습니다.")
            return
        
        print("\n🔧 API 상태 확인")
        print("-"*30)
        
        # 연결 테스트
        print("🔄 연결 테스트 중...")
        if self.gemini_api.test_connection():
            print("✅ API 연결 정상")
        else:
            print("❌ API 연결 실패")
        
        # 모델 정보
        info = self.gemini_api.get_model_info()
        print(f"\n📊 모델 정보:")
        print(f"  - 모델명: {info['model_name']}")
        print(f"  - API 키 설정: {'✅' if info['api_key_set'] else '❌'}")
        print(f"  - Temperature: {info['generation_config']['temperature']}")
        print(f"  - Max tokens: {info['generation_config']['max_output_tokens']}")
    
    def run(self):
        """프로그램 실행"""
        print("🤖 자동 글 변환 프로그램을 시작합니다...")
        
        # API 초기화
        if not self.initialize_api():
            print("프로그램을 종료합니다.")
            return
        
        # 메인 루프
        while True:
            self.display_menu()
            choice = input("메뉴를 선택하세요: ").strip()
            
            if choice == '1':
                self.transform_text()
            elif choice == '2':
                self.manage_guidelines()
            elif choice == '3':
                self.show_guidelines_list()
            elif choice == '4':
                self.set_current_guideline()
            elif choice == '5':
                self.check_api_status()
            elif choice == '0':
                print("👋 프로그램을 종료합니다.")
                break
            else:
                print("❌ 올바른 메뉴를 선택하세요.")

if __name__ == "__main__":
    app = TextTransformationApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 사용자에 의해 프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
        print("프로그램을 종료합니다.")