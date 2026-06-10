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

    def check_connectivity(self):
        """Performs a live handshake with Gemini to verify API key validity."""
        if self.client is None:
            return False, "Client not initialized."
        try:
            # Send a minimal prompt to verify the link
            self.client.models.generate_content(
                model=DEFAULT_GEMINI_MODEL,
                contents="Connectivity Test: Response 'OK' if active."
            )
            return True, "Handshake Successful: Neural Link Active."
        except Exception as e:
            error_msg = str(e).lower()
            if "401" in error_msg or "api_key_invalid" in error_msg:
                return False, "Handshake Failed: Invalid credential baseline."
            if "429" in error_msg or "quota" in error_msg:
                return False, "Handshake Failed: API rate limit active."
            if "404" in error_msg or "not found" in error_msg:
                return False, "Handshake Failed: Model target unavailable."
            if "location" in error_msg:
                return False, "Handshake Failed: Restricted regional access."
            return False, "Handshake Failed: Secure engine disconnect."

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
            if response and hasattr(response, 'text') and response.text:
                return response.text
            return "Neural Link Error: Silent response from forensic engine."
        except Exception as e:
            error_msg = str(e).lower()
            if "401" in error_msg or "api_key_invalid" in error_msg:
                return "Neural Link Error: Invalid credential baseline."
            if "429" in error_msg or "quota" in error_msg:
                return "Neural Link Error: API rate limit active."
            if "404" in error_msg or "not found" in error_msg:
                return "Neural Link Error: Model target unavailable."
            if "location" in error_msg:
                return "Neural Link Error: Restricted regional access."
            return "Neural Link Error: Secure engine disconnect."

@st.cache_resource
def get_ai_service():
    return AICharlieService()