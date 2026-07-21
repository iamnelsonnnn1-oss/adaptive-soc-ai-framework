import streamlit as st
import os

VERSION = "2.0-COCKPIT"


def _safe_secret(name: str):
    try:
        return st.secrets.get(name)
    except FileNotFoundError:
        return None


DEFAULT_GEMINI_MODEL = _safe_secret("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-1.5-flash"

def get_gemini_api_key():
    """Headless secret retrieval. No front-end entry allowed per protocol."""
    return (
        _safe_secret("GEMINI_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

ENABLE_LIVE_AWS = bool(_safe_secret("AWS_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID"))
ENABLE_AI_MENTOR = bool(get_gemini_api_key())

URGENCY_MAP = {
    "Low": {"label": "ADVISORY", "color": "#777777", "pulse": False},
    "Medium": {"label": "CAUTION", "color": "#FFBF00", "pulse": False},
    "High": {"label": "WARNING", "color": "#FF4B4B", "pulse": True},
    "Critical": {"label": "MASTER ALERT", "color": "#FF0000", "pulse": True}
}