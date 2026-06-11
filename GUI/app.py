import json
import os
import sys
import time

# Manually inject the local directory into sys.path to ensure module
# resolution (theme, settings, services) works correctly on Streamlit Cloud.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import pydeck as pdk
import streamlit as st

from ai import get_ai_service
from risk import get_risk_service
from scenarios import get_scenario_service
from settings import VERSION, URGENCY_MAP
from telemetry import get_telemetry_service
from theme import inject_cockpit_css


def initialize_cockpit() -> None:
    """Initialize baseline Streamlit session state for the cockpit."""
    if "cockpit_init" in st.session_state:
        return

    st.session_state.cockpit_init = True

    base_path = os.path.dirname(__file__)
    telemetry_file = os.path.join(base_path, "telemetry.json")

    if os.path.exists(telemetry_file):
        try:
            with open(telemetry_file, "r", encoding="utf-8") as f:
                st.session_state.threat_log = json.load(f)
        except Exception:
            st.session_state.threat_log = []
    else:
        st.session_state.threat_log = []

    st.session_state.chat_history = []
    st.session_state.points = 0
    st.session_state.assets_count = 1420
    st.session_state.ingestion_health = "98.4%"
    st.session_state.ai_charlie_state = "idle"
    st.session_state.sim_active = False
    st.session_state.last_sim_tick = time.time()
    st.session_state.sim_interval = 60


def handle_chat_global() -> None:
    """Handle AI Charlie input submission from session state."""
    query = st.session_state.get("ai_chatbot_input")
    if not query:
        return

    st.session_state.ai_charlie_state = "processing"
    try:
        threat_log = st.session_state.get("threat_log", []) or []
        latest = threat_log[0] if threat_log else {}
        forensics = latest.get("Forensics", {})
        enriched_context = (
            f"Vector: {latest.get('Vector', 'No active threat')}, "
            f"Evidence: {json.dumps(forensics)}"
        )

        ai_svc = get_ai_service()
        ai_resp = ai_svc.analyze_incident(query, enriched_context)

        st.session_state.chat_history.append(
            {"user": query, "ai": ai_resp}
        )
        st.session_state.ai_chatbot_input = ""
    finally:
        st.session_state.ai_charlie_state = "idle"


def render_ai_chatbot_interface(latest_threat_data: dict) -> None:
    """Render the AI Charlie analyst panel."""
    st.markdown("<div class='metric-label'>// AI Charlie Analyst</div>", unsafe_allow_html=True)

    st.markdown(
        (
            "<div style='height: 150px; overflow-y: auto; "
            "border: 1px solid rgba(0,255,0,0.1); padding: 10px; "
            "margin-bottom: 10px; font-family: monospace; "
            "font-size: 0.75rem; background: rgba(0,0,0,0.2);'>"
        ),
        unsafe_allow_html=True,
    )

    if not st.session_state.get("chat_history"):
        st.markdown("<div style='color: #444;'>[ STANDBY ]</div>", unsafe_allow_html=True)
    else:
        for chat in st.session_state.chat_history[-5:]:
            st.markdown(f"<div style='color: #888;'>USR: {chat['user']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #0F0; margin-bottom: 8px;'>AI: {chat['ai']}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    has_threat = bool(latest_threat_data)
    st.text_input(
        "NEURAL LINK COMMAND:",
        key="ai_chatbot_input",
        on_change=handle_chat_global,
        placeholder="Ask Charlie about this vector..." if has_threat else "Inject a threat to start analysis...",
        help="Type your question and press Enter.",
        disabled=not has_threat,
    )


def render_cockpit_header(threats: list, posture: dict, metrics: dict, ai_status: str) -> None:
    """Render the top flight-status strip."""
    alert_class = "alert-master" if posture.get("label") == "MASTER ALERT" else ""

    st.markdown(
        f"""
        <div class="flight-status-bar {alert_class}">
            <div style="display:flex; align-items:center;">
                <span style="color:#00FF00; font-weight:900; letter-spacing:3px; font-size:1.2rem;">
                    SECUREX COCKPIT
                </span>
                <span style="color:#555; margin-left:15px; font-size:0.7rem;">v{VERSION}</span>
            </div>
            <div style="display:flex; gap:40px;">
                <div style="text-align:center;">
                    <div class="metric-label">Active Incidents</div>
                    <div style="font-size:0.9rem; color:#FF4B4B; font-weight:bold;">{len(threats)}</div>
                </div>
                <div style="text-align:center;">
                    <div class="metric-label">Alert Velocity</div>
                    <div style="font-size:0.9rem; color:#00F5FF;">12/hr</div>
                </div>
                <div style="text-align:center;">
                    <div class="metric-label">Ingestion Health</div>
                    <div style="font-size:0.9rem; color:#00F5FF;">
                        <span class="ingestion-online"></span>{metrics.get('health_pct')}%
                    </div>
                </div>
                <div style="text-align:center;">
                    <div class="metric-label">Readiness</div>
                    <div style="font-size:0.9rem; color:#00F5FF;">{ai_status}</div>
                </div>
                <div style="text-align:center;">
                    <div class="metric-label">System Posture</div>
                    <div style="font-size:0.9rem; color:#00F5FF;">
                        {posture.get('rating')} [{posture.get('score')}]
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(threats: list, posture: dict, metrics: dict, ai_status: str) -> None:
    """Render top-level KPI cards."""
    critical_count = len([t for t in threats if t.get("Severity") == "Critical"])

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("ACTIVE INCIDENTS", len(threats))
    k2.metric("CRITICAL ALERTS", critical_count)
    k3.metric("POSTURE SCORE", f"{posture.get('score')}%", posture.get("rating"))
    k4.metric("INGESTION", f"{metrics.get('health_pct')}%", metrics.get("status"))
    k5.metric("AI READINESS", ai_status)


def render_dashboard() -> None:
    """Render the main dashboard view."""
    telemetry_svc = get_telemetry_service()
    risk_svc = get_risk_service()
    ai_svc = get_ai_service()

    threats = telemetry_svc.get_active_threats(st.session_state.get("threat_log", []))
    posture = risk_svc.calculate_score(threats)
    metrics = telemetry_svc.get_ingestion_metrics()
    ai_status = ai_svc.get_status()

    render_cockpit_header(threats, posture, metrics, ai_status)
    render_kpi_row(threats, posture, metrics, ai_status)

    st.info("Phase 1A dashboard rebuild in progress.")


def main() -> None:
    st.set_page_config(page_title="SECUREX Cyber Range", layout="wide", page_icon="🛡️")
    inject_cockpit_css()
    initialize_cockpit()

    with st.sidebar:
        logo_path = os.path.join(os.path.dirname(__file__), "securex.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")

        if os.path.exists(logo_path):
            st.image(logo_path, width=150)

        st.markdown(
            "<p style='text-align: center; color: #777;'>SECUREX COMMAND v3.0</p>",
            unsafe_allow_html=True,
        )

        nav = st.radio(
            "NAVIGATION",
            [
                "Dashboard",
                "Incident Queue",
                "Triage Console",
                "Playbooks / SOAR",
                "AI Threat Lab",
                "Research",
                "Scenario Control",
            ],
        )

        st.divider()

        st.session_state.sim_active = st.toggle(
            "Simulation Mode",
            value=st.session_state.sim_active,
        )

        if st.session_state.sim_active:
            scenario_svc = get_scenario_service()
            t_minus = scenario_svc.get_simulation_status(
                st.session_state.last_sim_tick,
                st.session_state.sim_interval,
            )
            st.metric("T-MINUS NEXT BREACH", f"{t_minus}s")

            if t_minus <= 0:
                new_inc = scenario_svc.generate_incident()
                st.session_state.threat_log.insert(0, new_inc)
                st.session_state.last_sim_tick = time.time()
                st.rerun()

    if nav == "Dashboard":
        render_dashboard()
    else:
        st.title(f"// {nav}")
        st.info(f"The {nav} module is scheduled for implementation in the next phase.")


if __name__ == "__main__":
    main()