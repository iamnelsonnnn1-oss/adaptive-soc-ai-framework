import pandas as pd
import json
import os
import streamlit as st
from datetime import datetime

class TelemetryService:
    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.local_file = os.path.join(self.base_path, "telemetry.json")

    def get_active_threats(self) -> list:
        """Retrieves and filters active threat vectors."""
        if os.path.exists(self.local_file):
            try:
                with open(self.local_file, "r") as f:
                    data = json.load(f)
                    return [t for t in data if t.get('Status') != 'Closed']
            except Exception:
                return []
        return []

    def get_ingestion_metrics(self):
        """Google SecOps style ingestion health metrics."""
        return {
            "status": "HEALTHY",
            "health_pct": 98.4,
            "throughput_kbps": 142.5,
            "last_sync": datetime.now().strftime("%H:%M:%S")
        }

@st.cache_resource
def get_telemetry_service():
    return TelemetryService()