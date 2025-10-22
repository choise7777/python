"""
프롬프트 시스템 - 사용자 지침에 따른 일관된 결과 생성
"""

import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

class PromptSystem:
    def __init__(self, guidelines_file: str = "guidelines.json"):
        """
        프롬프트 시스템 초기화
        
        Args:
            guidelines_file (str): 지침을 저장할 파일명
        """
        self.guidelines_file = guidelines_file
        self.guidelines = self._load_guidelines()
        
    def _load_guidelines(self) -> Dict[str, Any]:
        """
        저장된 지침 불러오기
        
        Returns:
            dict: 지침 딕셔너리
        """
        if os.path.exists(self.guidelines_file):
            try:
                with open(self.guidelines_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_guidelines(self):
        """지침을 파일에 저장"""
        try:
            with open(self.guidelines_file, 'w', encoding='utf-8') as f:
                json.dump(self.guidelines, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"지침 저장 중 오류: {str(e)}")
    
    def create_guideline(self, name: str, description: str, rules: List[str], 
                        examples: Optional[List[Dict[str, str]]] = None) -> bool:
        """
        새로운 지침 생성
        
        Args:
            name (str): 지침 이름
            description (str): 지침 설명
            rules (List[str]): 규칙 목록
            examples (List[Dict], optional): 예시 목록
            
        Returns:
            bool: 생성 성공 여부
        """
        try:
            guideline = {
                "name": name,
                "description": description,
                "rules": rules,
                "examples": examples or [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            self.guidelines[name] = guideline
            self._save_guidelines()
            return True
        except Exception as e:
            print(f"지침 생성 중 오류: {str(e)}")
            return False
    
    def update_guideline(self, name: str, **kwargs) -> bool:
        """
        기존 지침 업데이트
        
        Args:
            name (str): 지침 이름
            **kwargs: 업데이트할 필드들
            
        Returns:
            bool: 업데이트 성공 여부
        """
        if name not in self.guidelines:
            print(f"'{name}' 지침을 찾을 수 없습니다.")
            return False
        
        try:
            for key, value in kwargs.items():
                if key in ["description", "rules", "examples"]:
                    self.guidelines[name][key] = value
            
            self.guidelines[name]["updated_at"] = datetime.now().isoformat()
            self._save_guidelines()
            return True
        except Exception as e:
            print(f"지침 업데이트 중 오류: {str(e)}")
            return False
    
    def delete_guideline(self, name: str) -> bool:
        """
        지침 삭제
        
        Args:
            name (str): 삭제할 지침 이름
            
        Returns:
            bool: 삭제 성공 여부
        """
        if name in self.guidelines:
            del self.guidelines[name]
            self._save_guidelines()
            return True
        return False
    
    def get_guideline(self, name: str) -> Optional[Dict[str, Any]]:
        """
        특정 지침 반환
        
        Args:
            name (str): 지침 이름
            
        Returns:
            dict or None: 지침 정보
        """
        return self.guidelines.get(name)
    
    def list_guidelines(self) -> List[str]:
        """
        모든 지침 이름 목록 반환
        
        Returns:
            List[str]: 지침 이름 목록
        """
        return list(self.guidelines.keys())
    
    def build_prompt(self, guideline_name: str, user_input: str) -> str:
        """
        지침에 따른 프롬프트 구성
        
        Args:
            guideline_name (str): 사용할 지침 이름
            user_input (str): 사용자 입력
            
        Returns:
            str: 구성된 프롬프트
        """
        guideline = self.get_guideline(guideline_name)
        if not guideline:
            return f"오류: '{guideline_name}' 지침을 찾을 수 없습니다."
        
        prompt_parts = []
        
        # 지침 설명
        prompt_parts.append(f"**지침: {guideline['name']}**")
        prompt_parts.append(f"설명: {guideline['description']}")
        prompt_parts.append("")
        
        # 규칙들
        prompt_parts.append("**따라야 할 규칙들:**")
        for i, rule in enumerate(guideline['rules'], 1):
            prompt_parts.append(f"{i}. {rule}")
        prompt_parts.append("")
        
        # 예시들 (있는 경우)
        if guideline['examples']:
            prompt_parts.append("**예시:**")
            for i, example in enumerate(guideline['examples'], 1):
                prompt_parts.append(f"예시 {i}:")
                prompt_parts.append(f"입력: {example.get('input', '')}")
                prompt_parts.append(f"출력: {example.get('output', '')}")
                prompt_parts.append("")
        
        # 사용자 입력
        prompt_parts.append("**처리할 내용:**")
        prompt_parts.append(user_input)
        prompt_parts.append("")
        prompt_parts.append("위 지침과 규칙을 엄격히 따라 결과를 생성해주세요:")
        
        return "\n".join(prompt_parts)
    
    def get_guidelines_summary(self) -> str:
        """
        모든 지침의 요약 정보 반환
        
        Returns:
            str: 지침 요약
        """
        if not self.guidelines:
            return "저장된 지침이 없습니다."
        
        summary_parts = ["=== 저장된 지침 목록 ==="]
        for name, guideline in self.guidelines.items():
            summary_parts.append(f"\n📋 {name}")
            summary_parts.append(f"   설명: {guideline['description']}")
            summary_parts.append(f"   규칙 수: {len(guideline['rules'])}개")
            summary_parts.append(f"   예시 수: {len(guideline.get('examples', []))}개")
            summary_parts.append(f"   생성일: {guideline.get('created_at', 'Unknown')}")
        
        return "\n".join(summary_parts)

# 기본 지침 템플릿들
DEFAULT_GUIDELINES = {
    "유사문서회피_HTML생성": {
        "name": "유사문서회피 HTML 콘텐츠 생성",
        "description": "유사 문서에 걸리지 않도록 글을 재해석하여 HTML 형태로 변환하는 지침",
        "rules": [
            "원본 내용을 완전히 재해석하여 의미는 유지하되 표현을 완전히 다르게 작성",
            "HTML BODY 태그 내부 코드만 반환 (<!DOCTYPE>, <html>, <head>, <body> 태그 제외)",
            "공백 제외 최소 2500자 이상의 풍부한 내용으로 작성",
            "모든 CSS는 인라인 스타일로 작성 (예: <p style='color: #333; font-size: 16px;'>)",
            "사람이 직접 쓴 것처럼 자연스럽고 자유로운 문체 사용",
            "이모지는 사용하지 않음",
            "문단, 목록, 강조 등 다양한 HTML 구조 활용",
            "원본과 다른 관점이나 접근 방식으로 내용 재구성",
            "구체적인 예시나 부연 설명을 추가하여 분량 확장",
            "동의어나 유사 표현을 적극 활용하여 원문과 차별화"
        ],
        "examples": [
            {
                "input": "인공지능은 미래 기술의 핵심입니다.",
                "output": "<div style='max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; background-color: #f8f9fa; border-radius: 8px;'>\n<h2 style='color: #2c3e50; margin-bottom: 25px; font-size: 24px; border-bottom: 2px solid #3498db; padding-bottom: 10px; text-align: center;'>차세대 지능형 기술의 혁신적 전개</h2>\n<p style='line-height: 1.8; color: #34495e; font-size: 16px; margin-bottom: 20px; text-indent: 20px;'>현대 사회가 맞이한 기술 혁명의 중심에는 기계 학습과 딥러닝으로 대표되는 지능형 알고리즘이 자리하고 있습니다. 이러한 컴퓨터 인지 기술은 단순한 데이터 처리를 넘어서 인간의 사고 과정을 모방하고 때로는 능가하는 놀라운 성과를 보여주고 있습니다.</p>\n<ul style='color: #2c3e50; font-size: 15px; margin-bottom: 25px; padding-left: 30px;'>\n<li style='margin-bottom: 10px; line-height: 1.6;'>머신러닝 알고리즘의 진화적 발전과 실용적 적용</li>\n<li style='margin-bottom: 10px; line-height: 1.6;'>신경망 구조의 복잡성 증대와 처리 능력 향상</li>\n<li style='margin-bottom: 10px; line-height: 1.6;'>자율적 학습 시스템의 다양한 분야별 활용 확산</li>\n</ul>\n<p style='line-height: 1.8; color: #34495e; font-size: 16px; background-color: #ffffff; padding: 15px; border-left: 4px solid #3498db; margin-bottom: 20px;'>특히 주목할 점은 이런 스마트 기술들이 의료진단, 금융분석, 자동차 산업, 콘텐츠 제작 등 광범위한 영역에서 혁신적 변화를 주도하고 있다는 사실입니다.</p>\n</div>"
            }
        ],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
}