import pandas as pd
import json
import logging
import os
import streamlit as st
from datetime import datetime

logger = logging.getLogger(__name__)


class TelemetryError(Exception):
    """Raised when the telemetry source exists but cannot be read or parsed."""


class TelemetryService:
    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        self.local_file = os.path.join(self.base_path, "telemetry.json")

    def get_active_threats(self) -> list:
        """Retrieves and filters active threat vectors.

        A missing telemetry file is a valid state (no feed yet) and yields an
        empty list. A file that exists but is unreadable or malformed is NOT
        silently treated as "no threats" -- that would hide a broken feed as an
        all-clear on a security dashboard. Such failures are logged and raised
        as ``TelemetryError`` so callers can surface a degraded state.
        """
        if not os.path.exists(self.local_file):
            logger.info(
                "Telemetry source %s not found; reporting no active threats.",
                self.local_file,
            )
            return []

        try:
            with open(self.local_file, "r") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error(
                "Failed to read telemetry source %s: %s", self.local_file, exc
            )
            raise TelemetryError(
                f"Unable to load telemetry from {self.local_file}: {exc}"
            ) from exc

        if not isinstance(data, list):
            logger.error(
                "Telemetry source %s has unexpected shape %s; expected a list.",
                self.local_file,
                type(data).__name__,
            )
            raise TelemetryError(
                f"Telemetry source {self.local_file} must contain a JSON list, "
                f"got {type(data).__name__}."
            )

        return [t for t in data if isinstance(t, dict) and t.get("Status") != "Closed"]

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
