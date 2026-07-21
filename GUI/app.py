import os
import sys

import pandas as pd
import pydeck as pdk
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai import get_ai_service
from risk import get_risk_service
from settings import ENABLE_AI_MENTOR, ENABLE_LIVE_AWS, VERSION
from telemetry import get_telemetry_service
from theme import inject_cockpit_css


def initialize_state() -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_incident_id" not in st.session_state:
        st.session_state.selected_incident_id = None


def get_threats() -> list[dict]:
    return get_telemetry_service().get_active_threats()


def get_selected_threat(threats: list[dict]) -> dict | None:
    if not threats:
        st.session_state.selected_incident_id = None
        return None

    if st.session_state.selected_incident_id is None:
        st.session_state.selected_incident_id = threats[0].get("ID")

    selected = next(
        (threat for threat in threats if threat.get("ID") == st.session_state.selected_incident_id),
        None,
    )
    if selected is not None:
        return selected

    st.session_state.selected_incident_id = threats[0].get("ID")
    return threats[0]


def build_map_dataframe(threats: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(threats)
    if df.empty or not {"lat", "lon"}.issubset(df.columns):
        return pd.DataFrame()

    color_map = {
        "Critical": [255, 75, 75, 190],
        "High": [255, 191, 0, 180],
        "Medium": [0, 245, 255, 170],
        "Low": [120, 200, 255, 150],
    }
    df["color"] = df["Severity"].map(color_map).fillna([[0, 245, 255, 160]] * len(df))
    return df


def render_header(threats: list[dict], posture: dict, metrics: dict, ai_status: str) -> None:
    st.markdown(
        f"""
        <div class="flight-status-bar {'alert-master' if posture.get('label') == 'MASTER CAUTION' else ''}">
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="color:#00F5FF; font-weight:900; letter-spacing:2px; font-size:1.2rem;">
                    SECUREX COCKPIT
                </span>
                <span style="color:#777; font-size:0.8rem;">v{VERSION}</span>
            </div>
            <div style="display:flex; gap:28px; font-size:0.8rem;">
                <span>INCIDENTS: {len(threats)}</span>
                <span>POSTURE: {posture.get('rating')} [{posture.get('score')}]</span>
                <span>INGESTION: {metrics.get('health_pct')}%</span>
                <span>AI: {ai_status}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(threats: list[dict], posture: dict, metrics: dict, ai_status: str) -> None:
    critical_count = sum(1 for threat in threats if threat.get("Severity") == "Critical")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("ACTIVE INCIDENTS", len(threats))
    col2.metric("CRITICAL ALERTS", critical_count)
    col3.metric("POSTURE SCORE", f"{posture.get('score')}%", posture.get("rating"))
    col4.metric("INGESTION", f"{metrics.get('health_pct')}%", metrics.get("status"))
    col5.metric("AI READINESS", ai_status)


def render_map(threats: list[dict]) -> None:
    st.markdown("<div class='metric-label'>// Geospatial Threat Distribution</div>", unsafe_allow_html=True)
    map_df = build_map_dataframe(threats)
    if map_df.empty:
        st.info("No geospatial threat records are currently available.")
        return

    deck = pdk.Deck(
        map_style="dark",
        initial_view_state=pdk.ViewState(latitude=20, longitude=0, zoom=1.1, pitch=25),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position="[lon, lat]",
                get_fill_color="color",
                get_radius=220000,
                pickable=True,
            )
        ],
        tooltip={"text": "{ID}\n{Severity} | {Vector}\n{Status}"},
    )
    st.pydeck_chart(deck, use_container_width=True)


def render_incident_table(threats: list[dict]) -> None:
    st.markdown("<div class='metric-label'>// Active Incident Queue</div>", unsafe_allow_html=True)
    if not threats:
        st.info("No active incidents in the current demo feed.")
        return

    df = pd.DataFrame(threats)[["ID", "Severity", "Source", "Vector", "Status", "MITRE", "CVE"]]
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_incident_details(threat: dict | None) -> None:
    st.markdown("<div class='metric-label'>// Incident Detail</div>", unsafe_allow_html=True)
    if not threat:
        st.info("Select an incident to inspect its playbook and recovery steps.")
        return

    st.subheader(threat.get("Vector", "Unnamed Incident"))
    st.caption(f"{threat.get('ID', 'N/A')} · {threat.get('Severity', 'Unknown')} · {threat.get('Status', 'Unknown')}")
    st.write(threat.get("Insight", "No narrative provided."))

    st.markdown("**Playbook**")
    for step in threat.get("Playbook", []):
        st.write(f"- {step}")

    st.markdown("**Recovery Steps**")
    for step in threat.get("Steps", []):
        st.write(f"- {step}")

    st.markdown("**Report Prompts**")
    for question in threat.get("ReportQuestions", []):
        st.write(f"- {question}")


def render_ai_panel(threat: dict | None) -> None:
    st.markdown("<div class='metric-label'>// AI Charlie Analyst</div>", unsafe_allow_html=True)

    ai_service = get_ai_service()
    has_threat = threat is not None
    if not ENABLE_AI_MENTOR:
        st.warning("Gemini credentials are not configured. The dashboard remains online in degraded AI mode.")

    with st.form("ai-charlie-form", clear_on_submit=True):
        prompt = st.text_input(
            "NEURAL LINK COMMAND",
            disabled=not has_threat,
            placeholder="Ask Charlie how to triage this incident...",
        )
        submitted = st.form_submit_button("Send", use_container_width=True, disabled=not has_threat)

    if submitted and prompt and threat:
        context = (
            f"Vector: {threat.get('Vector', 'Unknown')}. "
            f"Severity: {threat.get('Severity', 'Unknown')}. "
            f"Insight: {threat.get('Insight', 'N/A')}."
        )
        response = ai_service.analyze_incident(prompt, context)
        st.session_state.chat_history.append({"user": prompt, "ai": response})

    if not st.session_state.chat_history:
        st.info("AI Charlie is ready once an incident is selected.")
        return

    for entry in reversed(st.session_state.chat_history[-4:]):
        st.markdown(f"**You:** {entry['user']}")
        st.markdown(f"**Charlie:** {entry['ai']}")


def render_sidebar(threats: list[dict], selected_threat: dict | None, ai_status: str, metrics: dict) -> None:
    with st.sidebar:
        logo_path = os.path.join(os.path.dirname(__file__), "securex.png")
        repo_logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=160)
        elif os.path.exists(repo_logo_path):
            st.image(repo_logo_path, width=160)

        st.markdown("### Recovery Console")
        st.caption("Online visual baseline for the maintenance window.")
        st.write(f"**AI status:** {ai_status}")
        st.write(f"**AWS link:** {'SECURE' if ENABLE_LIVE_AWS else 'UNLINKED'}")
        st.write(f"**Feed sync:** {metrics.get('last_sync', 'N/A')}")

        options = {threat.get("ID"): f"{threat.get('ID')} · {threat.get('Severity')} · {threat.get('Vector')}" for threat in threats}
        if options:
            current_id = selected_threat.get("ID") if selected_threat else next(iter(options))
            selected_id = st.selectbox(
                "Focus incident",
                options=list(options.keys()),
                index=list(options.keys()).index(current_id),
                format_func=lambda incident_id: options[incident_id],
            )
            st.session_state.selected_incident_id = selected_id
        else:
            st.info("No incidents available in the demo feed.")

        if st.button("Refresh telemetry", use_container_width=True):
            st.rerun()


def main() -> None:
    st.set_page_config(page_title="SECUREX Cyber Range", page_icon="🛡️", layout="wide")
    inject_cockpit_css()
    initialize_state()

    telemetry_service = get_telemetry_service()
    risk_service = get_risk_service()
    ai_service = get_ai_service()

    threats = get_threats()
    posture = risk_service.calculate_score(threats)
    metrics = telemetry_service.get_ingestion_metrics()
    ai_status = ai_service.get_status()
    selected_threat = get_selected_threat(threats)

    render_sidebar(threats, selected_threat, ai_status, metrics)
    render_header(threats, posture, metrics, ai_status)
    render_kpis(threats, posture, metrics, ai_status)

    left, right = st.columns([1.8, 1.1])
    with left:
        render_map(threats)
        render_incident_table(threats)
    with right:
        render_incident_details(selected_threat)
        st.divider()
        render_ai_panel(selected_threat)


if __name__ == "__main__":
    main()
