from google import genai
from settings import get_gemini_api_key, DEFAULT_GEMINI_MODEL
import streamlit as st

class AICharlieService:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def get_status(self):
        return "ONLINE" if self.client else "OFFLINE (DEGRADED)"

    def analyze_incident(self, query: str, context: str):
        if not self.client:
            return "AI Mentorship unavailable. Manual protocol suggested."
        
        try:
            prompt = (
                f"Act as AI Charlie, a Senior SOC Lead. Follow NIST SP 800-61 Rev. 2. "
                f"Context: {context}. Question: {query}. Keep it concise for a cockpit display."
            )
            response = self.client.models.generate_content(
                model=DEFAULT_GEMINI_MODEL,
                contents=prompt
            )
            return response.text if response.text else "Silent response from engine."
        except Exception as e:
            return f"Neural Link Error: {str(e)}"

@st.cache_resource
def get_ai_service():
    return AICharlieService()