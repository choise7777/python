"""
제미나이 API 연동 클래스
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List

class GeminiAPI:
    def __init__(self, api_key: Optional[str] = None, model_name: str = 'gemini-2.5-flash'):
        """
        제미나이 API 클래스 초기화
        
        Args:
            api_key (str, optional): API 키. None인 경우 환경변수에서 불러옴
            model_name (str): 사용할 모델 이름 (기본: gemini-2.5-flash)
        """
        # .env 파일 로드
        load_dotenv()
        
        # API 키 설정
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("API 키가 제공되지 않았습니다. .env 파일이나 매개변수로 API 키를 제공해주세요.")
        
        # 제미나이 설정
        genai.configure(api_key=self.api_key)
        
        # 모델 설정
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
        # 기본 설정
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 1,
            'top_k': 1,
            'max_output_tokens': 2048,
        }
        
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    
    def generate_text(self, prompt: str, custom_config: Optional[Dict[str, Any]] = None) -> str:
        """
        텍스트 생성
        
        Args:
            prompt (str): 입력 프롬프트
            custom_config (dict, optional): 사용자 정의 생성 설정
            
        Returns:
            str: 생성된 텍스트
        """
        try:
            # 설정 병합
            config = self.generation_config.copy()
            if custom_config:
                config.update(custom_config)
            
            # 텍스트 생성
            response = self.model.generate_content(
                prompt,
                generation_config=config,
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            print(f"텍스트 생성 중 오류 발생: {str(e)}")
            return f"오류: {str(e)}"
    
    def test_connection(self) -> bool:
        """
        API 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            response = self.generate_text("안녕하세요. 간단한 응답을 해주세요.")
            return len(response) > 0 and not response.startswith("오류:")
        except:
            return False
    
    def change_model(self, model_name: str) -> bool:
        """
        모델 변경
        
        Args:
            model_name (str): 새로운 모델 이름
            
        Returns:
            bool: 변경 성공 여부
        """
        try:
            self.model = genai.GenerativeModel(model_name)
            self.model_name = model_name
            return True
        except Exception as e:
            print(f"모델 변경 실패: {str(e)}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        사용 가능한 모델 목록 반환
        
        Returns:
            List[str]: 사용 가능한 모델 이름 목록
        """
        try:
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # models/ 접두사 제거
                    model_name = m.name.replace('models/', '')
                    models.append(model_name)
            return sorted(models)
        except Exception as e:
            print(f"모델 목록 가져오기 실패: {str(e)}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        모델 정보 반환
        
        Returns:
            dict: 모델 정보
        """
        return {
            "model_name": self.model_name,
            "generation_config": self.generation_config,
            "api_key_set": bool(self.api_key)
        }