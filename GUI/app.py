import pandas as pd
import streamlit as st
import random
import base64
import os
import pydeck as pdk
import json
from urllib.request import urlopen
from datetime import datetime


st.set_page_config(
    page_title="Adaptive SOC AI Framework",
    page_icon="🛡️",
    layout="wide",
)


def inject_custom_css(breach_active: bool = False) -> None:
    alert_style = '.stApp { animation: alert-flash 1.5s infinite !important; } @keyframes alert-flash { 0%, 100% { background-color: #000000; } 50% { background-color: #051a05; } }' if breach_active else ''
    ai_breach_style = '.ai-analyst-box { border: 2px solid #00FF00 !important; box-shadow: 0 0 30px rgba(0, 255, 0, 0.2) !important; transform: scale(1.01); transition: all 0.5s ease; }' if breach_active else ''
    spin_speed = "5s" if breach_active else "20s"
    st.markdown("""
        <style>
        /* Sovereign Canvas Reset & Corporate Depth */
        .stApp {
            background: 
                radial-gradient(circle at 50% 50%, #0a1118 0%, #000000 100%) !important;
            background-attachment: fixed !important;
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] {
            background-color: rgba(5, 8, 12, 0.8) !important;
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(0, 255, 0, 0.1) !important;
        }
        [data-testid="stSidebar"] label p {
            color: #FFFFFF !important;
            font-family: 'Courier New', monospace !important;
        }
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                linear-gradient(rgba(0, 255, 0, 0.015) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 0, 0.015) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
        }
        
        /* Tactical Font Injectors */
        h1, h2, h3, p, span, div {
            font-family: 'Courier New', monospace !important;
        }
        
        /* Glow Heartbeat Indicator */
        @keyframes pulse-green {
            0% { transform: scale(0.98); opacity: 0.5; box-shadow: 0 0 4px #00FF00; }
            50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 14px #00FF00; }
            100% { transform: scale(0.98); opacity: 0.5; box-shadow: 0 0 4px #00FF00; }
        }
        .status-pulse-commander {
            height: 10px;
            width: 10px;
            background-color: #00FF00;
            border-radius: 50%;
            display: inline-block;
            margin-right: 12px;
            animation: pulse-green 1.8s infinite ease-in-out;
        }

        /* Kinetic Globe Projection Control */
        .globe-texture-svg { 
            animation: globe-spin """ + spin_speed + """ linear infinite !important; 
            opacity: 0.4; 
        }
        @keyframes globe-spin { 
            0% { transform: translateX(0); } 100% { transform: translateX(-400px); } 
        }

        /* Global Anomaly Map Animations */
        @keyframes map-pulse {
            0% { r: 4; opacity: 1; }
            100% { r: 12; opacity: 0; }
        }
        .map-node-pulse {
            animation: map-pulse 2s infinite;
            fill: #00D1FF;
        }
        @keyframes dash-move {
            to { stroke-dashoffset: -20; }
        }
        .map-connection {
            stroke: #00D1FF;
            stroke-width: 1;
            stroke-dasharray: 4, 2;
            animation: dash-move 1s linear infinite;
            opacity: 0.3;
        }

        /* AI Analyst Box */
        .ai-analyst-box {
            background: rgba(10, 15, 24, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 0, 0.1);
            border-left: 4px solid #00FF00 !important;
            padding: 15px;
            margin-top: 20px; /* Ensure sufficient spacing from other elements */
        }
        
        /* High-Density Command Metric Containers */
        .pipeline-card {
            background: rgba(5, 5, 5, 0.6);
            backdrop-filter: blur(5px);
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 3px solid #00FF00;
            margin-bottom: 12px;
        }
        .pipeline-name {
            font-weight: bold;
            font-size: 0.85rem;
            color: #FFFFFF;
            letter-spacing: 1px;
        }
        .metric-value {
            color: #00FF00;
            font-weight: bold;
        }
        .secondary-text {
            color: #777777;
            font-size: 0.75rem;
        }
        
        /* Tactical Metric Overrides */
        div[data-testid="stMetric"], div.stMetric {
            background-color: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(0, 255, 0, 0.05) !important;
            padding: 20px !important;
            border-radius: 2px !important;
        }
        [data-testid="stMetricValue"] > div, .stMetricValue, .stMetricValue div {
            color: #00FF00 !important;
            font-family: 'Courier New', monospace !important;
            font-size: 2.2rem !important;
        }
        [data-testid="stMetricLabel"] > div, .stMetricLabel, .stMetricLabel div {
            color: #FFFFFF !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
        }
        /* Chronicle/Splunk Tactical UI Hardening */
        .analyst-terminal {
            background: rgba(0, 20, 0, 0.9);
            border: 1px solid #00FF00;
            padding: 15px;
            font-family: 'Courier New', monospace;
            color: #00FF00;
            height: 300px;
            overflow-y: auto;
            margin-bottom: 20px;
            box-shadow: inset 0 0 10px #00FF00;
        }
        
        @media (max-width: 768px) {
            .header-container { flex-direction: column !important; align-items: center !important; text-align: center !important; gap: 25px !important; width: 100% !important; }
            .logo-img { margin-right: 0 !important; margin-bottom: 15px !important; height: 90px !important; max-width: 100% !important; }
            .header-metrics { flex-direction: column !important; gap: 20px !important; align-items: center !important; width: 100% !important; justify-content: center !important; }
            .header-metrics > div { text-align: center !important; margin: 0 auto !important; }
            .ai-content-wrapper { flex-direction: column !important; gap: 25px !important; }
            .risk-score-box { width: 100% !important; border-left: none !important; border-top: 1px solid rgba(0, 255, 0, 0.2) !important; padding: 20px 0 0 0 !important; }
            .stMetric { width: 100% !important; }
            .map-container { height: 400px !important; }
        }
        /* Breach Simulation Overlay */
        """ + alert_style + """
        """ + ai_breach_style + """
        </style>
    """, unsafe_allow_html=True)


def get_system_health_data() -> dict:
    return {"cpu_percent": 42, "memory_percent": 68}


def get_active_threats_data() -> pd.DataFrame:
    # Protocol: Check for local telemetry file ingestion
    telemetry_path = os.path.join(os.path.dirname(__file__), "telemetry.json")
    local_data = []
    if os.path.exists(telemetry_path):
        try:
            with open(telemetry_path, "r") as f:
                local_data = json.load(f)
        except Exception:
            pass

    threat_pool = [
        {
            "ID": "TR-1081", "Severity": "Critical", "Source": "Suricata", "Vector": "Log4Shell RCE", "Status": "Active", "lat": 51.5074, "lon": -0.1278, "MITRE": "T1190", "CVE": "CVE-2021-44228", 
            "Playbook": ["Disable JNDI", "Patch Log4j", "WAF Filter"], "Correct": "Patch Log4j", 
            "DistractorExplanations": {
                "Disable JNDI": "Suboptimal. While it reduces surface area, the vulnerable library remains on disk and can be re-enabled.",
                "WAF Filter": "Ineffective. Polymorphic payloads use nesting like ${${lower:j}ndi} to bypass static WAF strings."
            },
            "Hint": "Look for the most permanent remediation that targets the library version itself.",
            "Steps": ["1. Identify all JAR files using Log4j < 2.17", "2. Update dependencies to latest patch", "3. Restart JVM instances."],
            "Insight": "Polymorphic payload detected. Obfuscated ${jndi:ldap} strings observed."
        },
        {
            "ID": "TR-1082", "Severity": "High", "Source": "EDR-Core", "Vector": "PwnKit Escalation", "Status": "Active", "lat": 48.8566, "lon": 2.3522, "MITRE": "T1068", "CVE": "CVE-2021-4034", 
            "Playbook": ["Remove SUID bit", "Patch Polkit", "Isolate Host"], "Correct": "Patch Polkit",
            "DistractorExplanations": {
                "Remove SUID bit": "Tactically sound but fragile. A system update might restore the bit, re-opening the hole.",
                "Isolate Host": "Overkill for a local privilege escalation if the workload is critical and patchable."
            },
            "Hint": "SUID bit removal is a temporary fix; what is the vendor-recommended path?",
            "Steps": ["1. Check polkit version", "2. Execute 'apt upgrade polkit'", "3. Verify pkexec permissions."],
            "Insight": "Metamorphic exploit: binary signature cycling detected in runtime."
        },
        {
            "ID": "TR-1083", "Severity": "Medium", "Source": "Kube-Sensor", "Vector": "runc Escape", "Status": "Active", "lat": 52.5200, "lon": 13.4050, "MITRE": "T1611", "CVE": "CVE-2024-21626", 
            "Playbook": ["Update Runc", "ReadOnly RootFS", "Pod Security Policy"], "Correct": "Update Runc",
            "DistractorExplanations": {
                "ReadOnly RootFS": "Bypassable. An escape via file descriptor can still allow interaction with the host.",
                "Pod Security Policy": "Admission controls don't fix a vulnerability already running in a container."
            },
            "Hint": "This is a core container runtime vulnerability. Focus on the engine.",
            "Steps": ["1. Drain affected K8s node", "2. Update libcontainer/runc package", "3. Un-drain and verify runtime."],
            "Insight": "Container escape via runc descriptor. Possible lateral movement."
        }
    ]
    
    if 'threat_log' not in st.session_state:
        initial_log = random.sample(threat_pool, 4)
        for item in initial_log:
            item["Time"] = datetime.now().strftime("%H:%M:%S")
        st.session_state.threat_log = initial_log

    return pd.DataFrame(st.session_state.threat_log)


def get_pipeline_status_data() -> pd.DataFrame:
    return pd.DataFrame([
        {"Pipeline": "Terraform Engine", "Status": "ACTIVE"},
        {"Pipeline": "Ansible Automation", "Status": "ACTIVE"},
        {"Pipeline": "Docker Runtime", "Status": "ACTIVE"},
        {"Pipeline": "Kubernetes Cluster", "Status": "ACTIVE"}
    ])


def render_header() -> None:
    logo_path = os.path.join(os.path.dirname(__file__), "securex.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")
    logo_html = ""
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
            logo_html = f'<img class="logo-img" src="data:image/png;base64,{logo_b64}" style="height:150px;margin-right:25px;vertical-align:middle;filter:drop-shadow(0 0 15px #00FF00);">'
    
    header_html = f'<div class="header-container" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;margin-bottom:30px;border-bottom:1px solid #1A1A1A;padding-bottom:20px;width:100%;"><div style="display:flex;align-items:center;flex-wrap:wrap;justify-content:center;">{logo_html}<div><h1 style="margin:0;font-family:\'Courier New\',monospace;font-size:2.2rem;font-weight:900;letter-spacing:4px;color:#00FF00;">SECUREX COMMAND</h1><p style="color:#FFFFFF;margin:5px 0 0 0;font-size:0.85rem;letter-spacing:1px;">[ SYSTEM INFRASTRUCTURE MONITORING V1.0 ]</p></div></div><div class="header-metrics" style="display:flex;gap:40px;align-items:center;flex-wrap:wrap;justify-content:center;"><div style="text-align:right;"><div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">THREATS TODAY</div><div style="color:#00FF00;font-weight:bold;font-size:1.2rem;">17</div></div><div style="text-align:right;"><div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">ASSETS MONITORED</div><div style="color:#FFFFFF;font-weight:bold;font-size:1.2rem;">2,491</div></div><div style="background:#000000;border:1px solid #00FF00;padding:8px 15px;"><span class="status-pulse-commander"></span><span style="color:#00FF00;font-weight:bold;font-size:0.8rem;letter-spacing:2px;font-family:\'Courier New\',monospace;">COMMAND CENTER ACTIVE</span></div></div></div>'
    st.markdown(header_html, unsafe_allow_html=True)


def render_system_health() -> None:
    health = get_system_health_data()
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// RESOURCE ALLOCATION</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("CPU Usage", f"{health['cpu_percent']}%")
    col2.metric("Memory", f"{health['memory_percent']}%")


def render_active_threats() -> None:
    threats = get_active_threats_data()
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// LIVE THREAT FEED</p>", unsafe_allow_html=True)
    for _, row in threats.iterrows():
        severity_color = {"Critical": "#00FF00", "High": "#FFFFFF", "Medium": "#777777", "Low": "#444444"}.get(row["Severity"], "#222222")
        threat_html = f'<div style="margin-bottom:12px;border-left:2px solid {severity_color};padding-left:10px;"><div style="font-size:0.75rem;color:#FFFFFF;">[{row["Time"]}] <span style="color:{severity_color};">{row["Source"]}</span></div><div style="font-size:0.8rem;color:#FFFFFF;font-weight:bold;">{row["Vector"]}</div><div style="font-size:0.7rem;color:#00FF00;margin-top:2px;font-family:\'Courier New\',monospace;"><a href="https://attack.mitre.org/techniques/{row["MITRE"]}/" target="_blank" style="color:#00FF00;text-decoration:none;">{row["MITRE"]}</a> | <a href="https://nvd.nist.gov/vuln/detail/{row["CVE"]}" target="_blank" style="color:#00FF00;text-decoration:none;">{row["CVE"]}</a></div></div>'
        st.markdown(threat_html, unsafe_allow_html=True)


def render_anomaly_map(zoom_lat=None, zoom_lon=None) -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// LIVE GEOSPATIAL TELEMETRY [ SATELLITE MODE ]</p>", unsafe_allow_html=True)

    # 1. Determine "Home" location
    try:
        url = 'http://ip-api.com/json'
        response = urlopen(url)
        data = json.load(response)
        curr_lat, curr_lon = data['lat'], data['lon']
    except:
        curr_lat, curr_lon = 51.5074, -0.1278

    threats = pd.DataFrame(st.session_state.threat_log).copy()
    threats['target_lat'] = curr_lat
    threats['target_lon'] = curr_lon

    # 2. Dynamic View Logic
    view_lat = zoom_lat if zoom_lat else curr_lat
    view_lon = zoom_lon if zoom_lon else curr_lon
    zoom_level = 8 if zoom_lat else 2

    # 3. ARC Layers for movement
    layers = [
        pdk.Layer(
            "ArcLayer",
            threats,
            get_source_position=["lon", "lat"],
            get_target_position=["target_lon", "target_lat"],
            get_source_color=[0, 255, 0, 120],
            get_target_color=[0, 255, 0, 255],
            get_width=5,
            pickable=True,
        ),
        pdk.Layer(
        "ScatterplotLayer",
        threats,
        get_position=["lon", "lat"],
        get_color="[0, 255, 0, 200]",
        get_radius=150000,
        pickable=True
        )
    ]

    view_state = pdk.ViewState(
        latitude=view_lat,
        longitude=view_lon,
        zoom=zoom_level,
        pitch=45,
    )
    
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/satellite-streets-v11",
        tooltip={"text": "ANOMALY: {Vector}\nCLICK SIDEBAR TO ANALYZE"}
    )
    
    st.pydeck_chart(r)


def render_ai_analyst() -> None:
    # Gamification State
    if 'points' not in st.session_state: st.session_state.points = 0
    
    ranks = ["PRIVATE", "COMMANDER 1", "COMMANDER 2", "COMMANDER 3", "COMMANDER 4", "COMMANDER 5", "COMMANDER 6", "COMMANDER 7", "OFFICERS CLUB"]
    rank_idx = min(st.session_state.points // 20, len(ranks) - 1)
    current_rank = ranks[rank_idx]

    threat_list = st.session_state.get('threat_log', [])
    if not threat_list:
        st.sidebar.success("ALL THREATS NEUTRALIZED. SECTOR CLEAR.")
        return

    latest = threat_list[0]

    # Custom Terminal Chat
    if 'show_intel' not in st.session_state: st.session_state.show_intel = False

    intel_guidance = ""
    if st.session_state.show_intel:
        intel_guidance = f"""
        <br><br>
        > 🤖 AI CHARLIE ANALYST: Intelligence required? Understood.<br>
        > RECOMMENDED CHANNELS:<br>
        > - <a href="https://attack.mitre.org/techniques/{latest['MITRE']}/" target="_blank" style="color:#00FF00;">MITRE ATT&CK: {latest['MITRE']}</a><br>
        > - <a href="https://nvd.nist.gov/vuln/detail/{latest['CVE']}" target="_blank" style="color:#00FF00;">NVD DETAILS: {latest['CVE']}</a><br>
        > - <a href="https://search.nist.gov/search?query={latest['CVE']}" target="_blank" style="color:#00FF00;">NIST SEARCH</a><br>
        -------------------------
        """

    st.sidebar.markdown(f"""
    <div class="analyst-terminal">
        > ACCESSING AI CHARLIE ANALYST...<br>
        > RANK: {current_rank}<br>
        > SCORE: {st.session_state.points} XP<br>
        -------------------------<br>
        > 🤖 AI CHARLIE ANALYST: Commander, we have a breach! {latest.get('Vector', 'Unknown')} detected.<br><br>
        > LOG: "{latest.get('Insight', 'Metadata unavailable for this vector.')}"{intel_guidance}{hint_text}{error_text}<br><br>
        > ADVISORY: Which playbook protocol should we initiate?
    </div>
    """, unsafe_allow_html=True)

    col_h1, col_h2 = st.sidebar.columns(2)
    if col_h1.button("📡 INTEL", key="intel_btn", use_container_width=True):
        st.session_state.show_intel = not st.session_state.show_intel; st.rerun()
    if col_h2.button("💡 HINT", key="hint_btn", use_container_width=True):
        st.session_state.show_hint = not st.session_state.show_hint; st.rerun()

    for action in latest.get('Playbook', []):
        if st.sidebar.button(f"EXECUTE: {action}", key=f"play_{latest['ID']}_{action}"):
            if action == latest.get('Correct'):
                st.balloons()
                st.session_state.points += 10; st.session_state.threat_log.pop(0)
                st.session_state.show_intel = False; st.session_state.show_hint = False; st.session_state.last_error = ""
                steps_fmt = "\\n".join(latest.get('Steps', []))
                st.sidebar.success(f"CORRECT. OPERATION COMPLETE.\\n\\nFIELD STEPS:\\n{steps_fmt}")
                st.rerun()
            else:
                st.session_state.last_error = latest.get('DistractorExplanations', {}).get(action, "Incorrect protocol selection.")
                st.rerun()


def render_pipeline_status() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// AUTOMATION HEALTH</p>", unsafe_allow_html=True)
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        card_html = f'<div class="pipeline-card"><div class="pipeline-name">{row["Pipeline"]}</div><div style="color:#00FF00;font-size:0.75rem;font-weight:bold;margin-top:4px;">● SECURE</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)


def main() -> None:
    if 'threat_log' not in st.session_state:
        st.session_state.threat_log = []
    if 'threat_count' not in st.session_state:
        st.session_state.threat_count = 0
    if 'assets_count' not in st.session_state:
        st.session_state.assets_count = 0

    with st.sidebar:
        render_ai_analyst()
        st.markdown("<p style='color: #FFFFFF; font-size: 0.7rem; letter-spacing: 1px;'>// TACTICAL SIMULATION</p>", unsafe_allow_html=True)
        breach_sim = st.toggle("SIMULATE SYSTEM BREACH", value=False)
        
        if st.button("INJECT DETECTION EVENT"):
            new_threat = random.choice(get_active_threats_data().to_dict('records')).copy()
            new_threat["ID"] = f"TR-{random.randint(2000, 9999)}"
            new_threat["Time"] = datetime.now().strftime("%H:%M:%S")
            # Prepend to keep latest on top
            st.session_state.threat_log = [new_threat] + st.session_state.threat_log[:9]
            st.session_state.threat_count += 1
            st.session_state.assets_count += random.randint(1, 5)
            st.rerun()

    # TACTICAL ENGINE
    threat_list = st.session_state.get('threat_log', [])
    latest_critical = next((t for t in threat_list if t.get("Severity") == "Critical"), None)
    active_breach_mode = breach_sim or (latest_critical is not None)

    inject_custom_css(breach_active=active_breach_mode)
    render_header(st.session_state.get('threat_count', 0), st.session_state.get('assets_count', 0))
    
    map_lat, map_lon = None, None
    if threat_list and len(threat_list) > 0:
        map_lat, map_lon = threat_list[0]['lat'], threat_list[0]['lon']

    # Main Command Deck
    col_left, col_center, col_right = st.columns([1.2, 4, 1.2])
    
    with col_left:
        render_active_threats()
        
    with col_center:
        render_anomaly_map(zoom_lat=map_lat, zoom_lon=map_lon)
        
    with col_right:
        render_pipeline_status()

    # Infrastructure Control Plane (Metrics moved to bottom for space)
    st.divider()
    render_system_health()


if __name__ == "__main__":
    main()
