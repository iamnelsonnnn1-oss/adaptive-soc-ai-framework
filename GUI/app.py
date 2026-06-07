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
        /* Mobile-First Responsive Overrides */
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
    threat_pool = [
        {"ID": "TR-1081", "Severity": "Critical", "Source": "Suricata", "Vector": "Log4Shell RCE", "Status": "Active", "lat": 51.5074, "lon": -0.1278, "MITRE": "T1190", "CVE": "CVE-2021-44228", "Playbook": ["Disable JNDI", "Patch Log4j", "WAF Filter"], "Insight": "Polymorphic payload detected. Attackers are obfuscating ${jndi:ldap} strings to bypass EDR filters."},
        {"ID": "TR-1082", "Severity": "High", "Source": "EDR-Core", "Vector": "PwnKit Escalation", "Status": "Active", "lat": 48.8566, "lon": 2.3522, "MITRE": "T1068", "CVE": "CVE-2021-4034", "Playbook": ["Remove SUID bit", "Patch Polkit", "Isolate Host"], "Insight": "Metamorphic exploit attempt. The binary signature is cycling every execution to evade signature-based detection."},
        {"ID": "TR-1083", "Severity": "Medium", "Source": "Kube-Sensor", "Vector": "runc Escape", "Status": "Active", "lat": 52.5200, "lon": 13.4050, "MITRE": "T1611", "CVE": "CVE-2024-21626", "Playbook": ["Update Runc", "ReadOnly RootFS", "Pod Security Policy"], "Insight": "Container escape detected. High-risk lateral movement to K8s control plane observed."},
        {"ID": "TR-1084", "Severity": "Critical", "Source": "Darktrace", "Vector": "MOVEit Transfer Exfil", "Status": "Active", "lat": 40.7128, "lon": -74.0060, "MITRE": "T1190", "CVE": "CVE-2023-34362", "Playbook": ["Disable SFTP", "Rotate DB Keys", "IP Blocklist"], "Insight": "Zero-day SQL injection in file transfer service. Immediate exfiltration detected in data-tier vpc."},
        {"ID": "TR-1085", "Severity": "High", "Source": "Falcon-X", "Vector": "PaperCut RCE", "Status": "Active", "lat": 34.0522, "lon": -118.2437, "MITRE": "T1210", "CVE": "CVE-2023-27350", "Playbook": ["Update Server", "Firewall Port 9191", "Kill Java Process"], "Insight": "Remote code execution via setup-mode bypass. Metamorphic shellcode payload detected in runtime memory."},
        {"ID": "TR-1089", "Severity": "Critical", "Source": "GuardDuty", "Vector": "Citrix Bleed", "Status": "Active", "lat": 1.3521, "lon": 103.8198, "MITRE": "T1190", "CVE": "CVE-2023-4966", "Playbook": ["Clear Sessions", "Update NetScaler", "Kill Active VPN"], "Insight": "Information disclosure vulnerability allowing session hijacking without credentials. Active session theft in progress."}
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

    # HQ Coordinates
    try:
        url = 'http://ip-api.com/json'
        response = urlopen(url)
        data = json.load(response)
        curr_lat, curr_lon = data['lat'], data['lon']
    except:
        curr_lat, curr_lon = 51.5074, -0.1278

    threats = get_active_threats_data().copy()
    threats['target_lat'] = curr_lat
    threats['target_lon'] = curr_lon

    # Dynamic View Logic
    view_lat = zoom_lat if zoom_lat else curr_lat
    view_lon = zoom_lon if zoom_lon else curr_lon
    zoom_level = 10 if zoom_lat else 2

    scatterplot = pdk.Layer(
        "ScatterplotLayer",
        threats,
        get_position=["lon", "lat"],
        get_color="[0, 255, 0, 160]",
        get_radius=150000,
        pickable=True
    )

    arclayer = pdk.Layer(
        "ArcLayer",
        threats,
        get_source_position=["lon", "lat"],
        get_target_position=["target_lon", "target_lat"],
        get_source_color=[0, 255, 0, 80],
        get_target_color=[0, 255, 0, 255],
        get_width=3,
        animation_speed=2,
    )

    view_state = pdk.ViewState(
        latitude=view_lat,
        longitude=view_lon,
        zoom=zoom_level,
        pitch=45,
    )
    
    r = pdk.Deck(
        layers=[arclayer, scatterplot],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/satellite-streets-v11",
        tooltip={"text": "Anomaly: {Vector}\nSource: {Source}"}
    )
    
    st.pydeck_chart(r)


def render_ai_analyst() -> None:
    threat_list = st.session_state.get('threat_log', [])
    if not threat_list: return

    latest = threat_list[0]

    st.markdown(f"""
    <div class="ai-analyst-box">
        <div style="color:#00FF00;font-weight:bold;font-size:0.9rem;margin-bottom:15px;">🤖 AI CHARLIE // SOC CO-PILOT ACTIVE</div>
        <div class="ai-content-wrapper" style="display:flex;gap:30px;flex-wrap:wrap;">
            <div style="flex:1;min-width:280px;">
                <p style="color:#FFFFFF;font-size:0.9rem;font-weight:bold;margin-bottom:5px;">VECTOR: {latest['Vector']}</p>
                <p style="color:#AAAAAA;font-size:0.85rem;line-height:1.6;">"{latest['Insight']}"</p>
            </div>
            <div class="risk-score-box" style="width:220px;border-left:1px solid rgba(0,255,0,0.2);padding-left:20px;">
                <div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">INCIDENT RISK</div>
                <div style="color:#00FF00;font-size:2rem;font-weight:bold;">{random.randint(85, 99)}/100</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='color: #00FF00; font-size: 0.7rem; margin-top: 15px;'>// STUDENT ACTION: SELECT REMEDIATION PLAYBOOK</p>", unsafe_allow_html=True)
    playbook_cols = st.columns(len(latest['Playbook']))
    for i, action in enumerate(latest['Playbook']):
        if playbook_cols[i].button(action, use_container_width=True, key=f"play_{latest['ID']}_{i}"):
            st.balloons()
            st.success(f"SUCCESS: {action} EXECUTED.")
            st.session_state.threat_log.pop(0)
            st.rerun()


def render_pipeline_status() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// AUTOMATION HEALTH</p>", unsafe_allow_html=True)
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        card_html = f'<div class="pipeline-card"><div class="pipeline-name">{row["Pipeline"]}</div><div style="color:#00FF00;font-size:0.75rem;font-weight:bold;margin-top:4px;">● SECURE</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)


def main() -> None:
    # Command Simulation State
    with st.sidebar:
        st.markdown("<p style='color: #FFFFFF; font-size: 0.7rem; letter-spacing: 1px;'>// TACTICAL SIMULATION</p>", unsafe_allow_html=True)
        breach_sim = st.toggle("SIMULATE SYSTEM BREACH", value=False)
        
        if st.button("INJECT DETECTION EVENT"):
            new_threat = random.choice(get_active_threats_data().to_dict('records')).copy()
            new_threat["ID"] = f"TR-{random.randint(2000, 9999)}"
            new_threat["Time"] = datetime.now().strftime("%H:%M:%S")
            # Prepend to keep latest on top
            st.session_state.threat_log = [new_threat] + st.session_state.threat_log[:9]
            st.rerun()

    # Automatic Breach Trigger Logic
    critical_threat_active = any(t.get("Severity") == "Critical" for t in st.session_state.get('threat_log', []))
    active_breach_mode = breach_sim or critical_threat_active

    inject_custom_css(breach_active=active_breach_mode)
    render_header()
    
    # Main Command Deck
    col_left, col_center, col_right = st.columns([1.2, 4, 1.2])
    
    with col_left:
        render_active_threats()
        
    with col_center:
        render_anomaly_map()
        
    with col_right:
        render_pipeline_status()

    # Infrastructure Control Plane (Metrics moved to bottom for space)
    st.divider()
    render_system_health()
    render_ai_analyst()


if __name__ == "__main__":
    main()
