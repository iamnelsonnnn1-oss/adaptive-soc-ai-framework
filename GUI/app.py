import streamlit as st
from theme import inject_cockpit_css
from settings import VERSION, URGENCY_MAP
from ai import get_ai_service
from telemetry import get_telemetry_service
from risk import get_risk_service
import time
import os
import json
import pandas as pd
import pydeck as pdk

def initialize_cockpit():
    """Master initialization for the cockpit state."""
    if 'cockpit_init' not in st.session_state:
        st.session_state.cockpit_init = True
        # Load baseline telemetry from JSON
        base_path = os.path.dirname(__file__)
        telemetry_file = os.path.join(base_path, "telemetry.json")
        if os.path.exists(telemetry_file):
            try:
                with open(telemetry_file, "r") as f:
                    st.session_state.threat_log = json.load(f)
            except Exception:
                st.session_state.threat_log = []
        else:
            st.session_state.threat_log = []
            
        st.session_state.chat_history = []
        st.session_state.points = 0
        st.session_state.assets_count = 1420  # Baseline monitored assets
        st.session_state.ingestion_health = "98.4%"
        st.session_state.ai_charlie_state = "idle"

def handle_chat_global():
    """Global handler for AI Charlie chat input."""
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
        st.session_state.chat_history.append({"user": query, "ai": ai_resp})
        st.session_state.ai_chatbot_input = ""
    finally:
        st.session_state.ai_charlie_state = "idle"

def render_ai_chatbot_interface(latest_threat_data: dict) -> None:
    """Renders the dedicated interface for the AI Charlie chatbot."""
    st.markdown("<div class='metric-label'>// AI Charlie Analyst</div>", unsafe_allow_html=True)
    
    # Console-style chat history view
    st.markdown("<div style='height: 150px; overflow-y: auto; border: 1px solid rgba(0,255,0,0.1); padding: 10px; margin-bottom: 10px; font-family: monospace; font-size: 0.75rem; background: rgba(0,0,0,0.2);'>", unsafe_allow_html=True)
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

def render_cockpit_header():
    """TOP STRIP: Flight Status Bar."""
    ai_svc = get_ai_service()
    telemetry_svc = get_telemetry_service()
    risk_svc = get_risk_service()
    
    threats = telemetry_svc.get_active_threats()
    posture = risk_svc.calculate_score(threats)
    metrics = telemetry_svc.get_ingestion_metrics()
    
    alert_class = "alert-master" if posture['label'] == "MASTER CAUTION" else ""
    
    st.markdown(f"""
        <div class="flight-status-bar {alert_class}">
            <div style="display:flex; align-items:center;">
                <span style="color:#00FF00; font-weight:900; letter-spacing:3px; font-size:1.2rem;">SECUREX COCKPIT</span>
                <span style="color:#555; margin-left:15px; font-size:0.7rem;">v{VERSION}</span>
            </div>
            <div style="display:flex; gap:40px;">
                <div style="text-align:center;">
                    <div class="metric-label">Ingestion Health</div>
                    <div style="font-size:0.9rem; color:#00FF00;"><span class="ingestion-online"></span>{metrics['health_pct']}%</div>
                </div>
                <div style="text-align:center;">
                    <div class="metric-label">AI Analyst</div>
                    <div style="font-size:0.9rem; color:#00FF00;">{ai_svc.get_status()}</div>
                </div>
                <div style="text-align:center;">
                    <div class="metric-label">Posture Score</div>
                    <div style="font-size:0.9rem; color:#00FF00;">{posture['rating']} ({posture['score']})</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="SECUREX COCKPIT", layout="wide")
    inject_cockpit_css()
    initialize_cockpit()
    
    render_cockpit_header()
    
    # Fetch live data from services
    telemetry_svc = get_telemetry_service()
    threats = telemetry_svc.get_active_threats()

    # --- COCKPIT 4-TIER GRID ---
    col_radar, col_glass, col_console = st.columns([1, 2.5, 1])

    with col_radar:
        st.markdown("<div class='metric-label'>// Threat Radar (Active Vectors)</div>", unsafe_allow_html=True)
        if not threats:
            st.markdown("<div class='radar-terminal' style='color:#777;'>[SCANNING SECTOR...]<br>No active vectors detected.</div>", unsafe_allow_html=True)
        else:
            radar_html = ""
            for t in threats:
                color = "#FF0000" if t['Severity'] == "Critical" else "#FFBF00" if t['Severity'] == "High" else "#00FF00"
                radar_html += f"<div style='margin-bottom:10px; border-left:2px solid {color}; padding-left:10px;'>"
                radar_html += f"<span style='color:{color}; font-size:0.65rem;'>{t['Severity'].upper()}</span><br>"
                radar_html += f"<span style='color:#EEE; font-size:0.8rem;'>{t['Vector']}</span>"
                radar_html += "</div>"
            st.markdown(f"<div class='radar-terminal'>{radar_html}</div>", unsafe_allow_html=True)
            
        st.divider()
        st.markdown("<div class='metric-label'>// Urgency Buckets</div>", unsafe_allow_html=True)
        crit_count = len([t for t in threats if t['Severity'] == 'Critical'])
        high_count = len([t for t in threats if t['Severity'] == 'High'])
        st.progress(min(1.0, crit_count/5), text=f"CRITICAL ({crit_count})")
        st.progress(min(1.0, high_count/10), text=f"HIGH ({high_count})")

    with col_glass:
        st.markdown("<div class='metric-label'>// Tactical Glass Display</div>", unsafe_allow_html=True)
        
        # Integrated pydeck Geospatial Mapping
        df = pd.DataFrame(threats)
        if not df.empty:
            view_state = pdk.ViewState(latitude=30, longitude=0, zoom=1, pitch=45)
            layer = pdk.Layer(
                "ScatterplotLayer",
                df,
                get_position=["lon", "lat"],
                get_color="[255, 0, 0, 160]",
                get_radius=200000,
            )
            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                map_style="mapbox://styles/mapbox/dark-v9"
            ))
        else:
            st.image("https://raw.githubusercontent.com/visgl/deck.gl-data/master/images/whats-new/h3-hexagon-layer.png", 
                     caption="GEOSPATIAL ANOMALY MAP (SIMULATED)", use_container_width=True)
        
        st.markdown("<div class='metric-label'>// Detection Velocity</div>", unsafe_allow_html=True)
        st.line_chart([10, 15, 8, 12, 5, 20], color="#00F5FF")

    with col_console:
        st.markdown("<div class='metric-label'>// Switchgear & Action Rail</div>", unsafe_allow_html=True)
        # Buttons active only if threats exist
        has_data = len(threats) > 0
        st.button("⚡ ISOLATE HOST", disabled=not has_data, use_container_width=True)
        st.button("🔍 ENRICH ARTIFACT", disabled=not has_data, use_container_width=True)
        st.button("📂 OPEN CASE", disabled=not has_data, use_container_width=True)
        
        if st.button("📡 TEST NEURAL LINK", use_container_width=True):
            ai_svc = get_ai_service()
            with st.spinner("Initiating handshake..."):
                success, message = ai_svc.check_connectivity()
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        st.divider()
        # Integrated state-safe AI mentorship interface
        render_ai_chatbot_interface(threats[0] if threats else {})
        
        st.divider()
        st.markdown("<div class='metric-label'>// Cloud Link Status</div>", unsafe_allow_html=True)
        aws_status = "SECURE" if st.secrets.get("AWS_ACCESS_KEY_ID") else "UNLINKED"
        st.write(f"AWS EU-CENTRAL-1: {aws_status}")

    st.divider()
    st.markdown("<div class='metric-label'>// Mission Timeline</div>", unsafe_allow_html=True)
    for t in threats[:2]: # Display up to 2 latest threats
        time_str = t.get('Time', 'N/A')
        vector_str = t.get('Vector', 'Unknown Vector')
        source_str = t.get('Source', 'Unknown Source')
        st.markdown(f"<div class='timeline-entry' style='color:#00F5FF;'>[ {time_str} ] Detection: {vector_str} detected via {source_str}</div>", unsafe_allow_html=True)
    st.markdown("<div class='timeline-entry'>[ 00:00:01 ] Cockpit initialized. Master systems online.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
