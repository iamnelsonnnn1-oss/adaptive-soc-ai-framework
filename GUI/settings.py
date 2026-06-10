import streamlit as st
import os

# --- VENDOR ALIGNMENT: GOOGLE SECOPS & SPLUNK ES ---
VERSION = "2.0-COCKPIT"
DEFAULT_GEMINI_MODEL = st.secrets.get("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-1.5-flash"

# --- FEATURE FLAGS ---
ENABLE_LIVE_AWS = bool(st.secrets.get("AWS_ACCESS_KEY_ID"))
ENABLE_AI_MENTOR = bool(st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY"))

# --- AVIATION ALERTING HIERARCHY ---
URGENCY_MAP = {
    "Low": {"label": "ADVISORY", "color": "#777777", "pulse": False},
    "Medium": {"label": "CAUTION", "color": "#FFBF00", "pulse": False},
    "High": {"label": "WARNING", "color": "#FF4B4B", "pulse": True},
    "Critical": {"label": "MASTER ALERT", "color": "#FF0000", "pulse": True}
}

def get_gemini_api_key():
    """Headless secret retrieval. No front-end entry allowed per protocol."""
    return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

def get_aws_credentials():
    return {
        "access_key": st.secrets.get("AWS_ACCESS_KEY_ID"),
        "secret_key": st.secrets.get("AWS_SECRET_ACCESS_KEY"),
        "region": st.secrets.get("AWS_DEFAULT_REGION", "eu-central-1")
    }