import streamlit as st
from theme import inject_cockpit_css
from settings import VERSION
from ai import get_ai_service
import time

def initialize_cockpit():
    """Master initialization for the cockpit state."""
    if 'cockpit_init' not in st.session_state:
        st.session_state.cockpit_init = True
        st.session_state.threat_log = []
        st.session_state.chat_history = []
        st.session_state.points = 0
        st.session_state.assets_count = 1420  # Baseline monitored assets
        st.session_state.ingestion_health = "98.4%"

def render_cockpit_header():
    """TOP STRIP: Flight Status Bar."""
    ai_svc = get_ai_service()
    st.markdown(f"""
        <div class="flight-status-bar">
            <div style="display:flex; align-items:center;">
                <span style="color:#00FF00; font-weight:900; letter-spacing:3px; font-size:1.2rem;">SECUREX COCKPIT</span>
                <span style="color:#555; margin-left:15px; font-size:0.7rem;">v{VERSION}</span>
            </div>
            <div style="display:flex; gap:30px;">
                <div style="text-align:center;">
                    <div class="metric-label">Ingestion Health</div>
                    <div style="font-size:0.9rem; color:#00FF00;"><span class="ingestion-online"></span>{st.session_state.ingestion_health}</div>
                </div>
                <div style="text-align:center;">
                    <div class="metric-label">AI Analyst</div>
                    <div style="font-size:0.9rem; color:#00FF00;">{ai_svc.get_status()}</div>
                </div>
                <div style="text-align:center;">
                    <div class="metric-label">Posture Score</div>
                    <div style="font-size:0.9rem; color:#00FF00;">GOLD</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="SECUREX COCKPIT", layout="wide")
    inject_cockpit_css()
    initialize_cockpit()
    
    render_cockpit_header()

    # --- COCKPIT 4-TIER GRID ---
    # 1. Left: Threat Radar
    # 2. Center: Tactical Glass (Wide)
    # 3. Right: Action console
    col_radar, col_glass, col_console = st.columns([1, 2.5, 1])

    with col_radar:
        st.markdown("<div class='metric-label'>// Threat Radar</div>", unsafe_allow_html=True)
        st.markdown("<div class='radar-terminal' style='color:#777;'>[SCANNING SECTOR...]<br>No active vectors detected.</div>", unsafe_allow_html=True)
        st.divider()
        st.markdown("<div class='metric-label'>// Urgency Buckets</div>", unsafe_allow_html=True)
        st.progress(0, text="CRITICAL")
        st.progress(0, text="HIGH")

    with col_glass:
        st.markdown("<div class='metric-label'>// Tactical Glass Display</div>", unsafe_allow_html=True)
        # Placeholder for Map / Relationship Graph
        st.image("https://raw.githubusercontent.com/visgl/deck.gl-data/master/images/whats-new/h3-hexagon-layer.png", 
                 caption="GEOSPATIAL ANOMALY MAP (SIMULATED)", use_container_width=True)
        
        st.markdown("<div class='metric-label'>// Detection Velocity</div>", unsafe_allow_html=True)
        st.line_chart([10, 15, 8, 12, 5, 20], color="#00FF00")

    with col_console:
        st.markdown("<div class='metric-label'>// System Switchgear</div>", unsafe_allow_html=True)
        st.button("⚡ ISOLATE HOST", disabled=True)
        st.button("🔍 ENRICH ARTIFACT", disabled=True)
        st.button("📂 OPEN CASE", disabled=True)
        st.button("🤖 AI ASSIST", disabled=True)
        st.divider()
        st.markdown("<div class='metric-label'>// Cloud Link Status</div>", unsafe_allow_html=True)
        st.write("AWS EU-CENTRAL-1: SECURE")

    st.markdown("<div class='metric-label'>// Mission Timeline</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='timeline-entry' style='color:#00FF00;'>[ 00:00:01 ] Cockpit initialized. Master systems online.</div>
        <div class='timeline-entry'>[ 00:00:05 ] Telemetry ingestion stable. Monitoring Gold Baseline.</div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
