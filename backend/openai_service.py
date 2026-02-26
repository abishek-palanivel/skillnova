"""
Google Gemini AI Service - Free AI Integration
"""
import os
from google import genai
from google.genai import types
from typing import Dict, List, Any, Optional
import json

class GeminiAIService:
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found in environment variables")
            print("AI features will use fallback templates. Set GEMINI_API_KEY in .env for full AI functionality.")
            self.client = None
            self.model_id = None
            return
        
        try:
            self.client = genai.Client(api_key=api_key)
            self.model_id = 'gemini-2.0-flash-exp'  # Latest free model
        except Exception as e:
            print(f"WARNING: Failed to initialize Gemini client: {e}")
            print("AI features will use fallback templates.")
            self.client = None
            self.model_id = None
        
    def generate_completion(self, prompt: str, system_message: str = None, 
                          temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate a completion using Google Gemini API"""
        if not self.client:
            return None
            
        try:
            # Combine system message and prompt
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return None
    
    def generate_json_completion(self, prompt: str, system_message: str = None,
                                temperature: float = 0.7) -> Optional[Dict]:
        """Generate a JSON response using Google Gemini API"""
        if not self.client:
            return None
            
        try:
            # Add JSON instruction to prompt
            json_prompt = f"{prompt}\n\nIMPORTANT: Respond ONLY with valid JSON. No other text."
            
            full_prompt = json_prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{json_prompt}"
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=2000,
                    response_mime_type="application/json"
                )
            )
            
            content = response.text.strip()
            
            # Extract JSON from markdown code blocks if present
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"Gemini JSON API Error: {str(e)}")
            return None

# Global instance
gemini_service = GeminiAIService()
