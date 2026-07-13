import logging

from google import genai
from settings import get_gemini_api_key, DEFAULT_GEMINI_MODEL
import streamlit as st

logger = logging.getLogger(__name__)


def _classify_error(exc: Exception) -> str:
    """Maps a raw Gemini exception to a concise cockpit-friendly reason."""
    error_msg = str(exc).lower()
    if "401" in error_msg or "api_key_invalid" in error_msg:
        return "Invalid credential baseline."
    if "429" in error_msg or "quota" in error_msg:
        return "API rate limit active."
    if "404" in error_msg or "not found" in error_msg:
        return "Model target unavailable."
    if "location" in error_msg:
        return "Restricted regional access."
    return "Secure engine disconnect."


class AICharlieService:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        self.client = None
        self.init_error = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as exc:
                # Degraded operation is intentional, but the reason must not be
                # swallowed silently -- log it so operators can diagnose.
                self.init_error = str(exc)
                logger.exception("Failed to initialize Gemini client: %s", exc)
                self.client = None

    def get_status(self):
        return "ONLINE" if self.client else "OFFLINE (DEGRADED)"

    def check_connectivity(self):
        """
        Performs a live handshake with Gemini to verify API key validity.
        This method is required by the switchgear console in app.py.
        """
        if self.client is None:
            return False, "Client not initialized."
        try:
            # Send a minimal prompt to verify the link
            self.client.models.generate_content(
                model=DEFAULT_GEMINI_MODEL,
                contents="Connectivity Test: Response 'OK' if active."
            )
            return True, "Handshake Successful: Neural Link Active."
        except Exception as exc:
            logger.warning("Gemini connectivity check failed: %s", exc)
            return False, f"Handshake Failed: {_classify_error(exc)}"

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
            logger.warning("Gemini returned an empty response for incident analysis.")
            return "Neural Link Error: Silent response from forensic engine."
        except Exception as exc:
            logger.warning("Gemini incident analysis failed: %s", exc)
            return f"Neural Link Error: {_classify_error(exc)}"

@st.cache_resource
def get_ai_service():
    return AICharlieService()
