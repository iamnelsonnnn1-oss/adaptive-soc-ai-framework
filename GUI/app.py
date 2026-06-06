import pandas as pd
import streamlit as st
import random
import base64
import os
from datetime import datetime


st.set_page_config(
    page_title="Adaptive SOC AI Framework",
    page_icon="🛡️",
    layout="wide",
)


def inject_custom_css(breach_active: bool = False) -> None:
    alert_style = '.stApp { animation: alert-flash 2s infinite !important; } @keyframes alert-flash { 0%, 100% { background-color: #000000; } 50% { background-color: #001a00; } }' if breach_active else ''
    ai_breach_style = '.ai-analyst-box { border-left: 4px solid #00FF00 !important; border: 1px solid #00FF00 !important; box-shadow: 0 0 15px rgba(0, 255, 0, 0.4) !important; }' if breach_active else ''
    st.markdown("""
        <style>
        /* Sovereign Canvas Reset */
        .stApp {
            background-color: #000000 !important;
            color: #FFFFFF !important;
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
            background: #0A0A0A;
            border: 1px solid #1A1A1A;
            border-left: 4px solid #00FF00;
            padding: 15px;
            margin-top: 20px; /* Ensure sufficient spacing from other elements */
        }
        
        /* High-Density Command Metric Containers */
        .pipeline-card {
            background: #050505;
            padding: 10px;
            border: 1px solid #1A1A1A;
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
            background-color: #000000 !important;
            border: 1px solid #1A1A1A !important;
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
        /* Breach Simulation Overlay */
        """ + alert_style + """
        """ + ai_breach_style + """
        </style>
    """, unsafe_allow_html=True)


def get_system_health_data() -> dict:
    return {"cpu_percent": 42, "memory_percent": 68}


def get_active_threats_data() -> pd.DataFrame:
    threat_pool = [
        {"ID": "TR-1081", "Severity": "Critical", "Source": "Suricata", "Vector": "Exfiltration", "Status": "Intercepted"},
        {"ID": "TR-1082", "Severity": "High", "Source": "Core Defense", "Vector": "Privilege Esc", "Status": "Isolating"},
        {"ID": "TR-1083", "Severity": "Medium", "Source": "Kube-Linter", "Vector": "Misconfig", "Status": "Triaged"},
        {"ID": "TR-1084", "Severity": "Critical", "Source": "Darktrace", "Vector": "Beaconing", "Status": "Blocking"},
        {"ID": "TR-1085", "Severity": "High", "Source": "LimaCharlie", "Vector": "Ransomware-IOA", "Status": "Killing"},
        {"ID": "TR-1086", "Severity": "Medium", "Source": "Suricata", "Vector": "SQL Injection", "Status": "Logged"},
        {"ID": "TR-1087", "Severity": "Low", "Source": "Kube-Linter", "Vector": "Root Container", "Status": "Triaged"},
        {"ID": "TR-1088", "Severity": "High", "Source": "CloudTrail", "Vector": "Credential Theft", "Status": "Suspending"},
        {"ID": "TR-1089", "Severity": "Critical", "Source": "GuardDuty", "Vector": "DDoS Ingress", "Status": "Filtering"}
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
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:150px;margin-right:25px;vertical-align:middle;filter:drop-shadow(0 0 15px #00FF00);">'
    
    header_html = f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:30px;border-bottom:1px solid #1A1A1A;padding-bottom:20px;"><div style="display:flex;align-items:center;">{logo_html}<div><h1 style="margin:0;font-family:\'Courier New\',monospace;font-size:2.2rem;font-weight:900;letter-spacing:4px;color:#00FF00;">SECUREX COMMAND</h1><p style="color:#FFFFFF;margin:5px 0 0 0;font-size:0.85rem;letter-spacing:1px;">[ SYSTEM INFRASTRUCTURE MONITORING V1.0 ]</p></div></div><div style="display:flex;gap:40px;align-items:center;"><div style="text-align:right;"><div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">THREATS TODAY</div><div style="color:#00FF00;font-weight:bold;font-size:1.2rem;">17</div></div><div style="text-align:right;"><div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">ASSETS MONITORED</div><div style="color:#FFFFFF;font-weight:bold;font-size:1.2rem;">2,491</div></div><div style="background:#000000;border:1px solid #00FF00;padding:8px 15px;"><span class="status-pulse-commander"></span><span style="color:#00FF00;font-weight:bold;font-size:0.8rem;letter-spacing:2px;font-family:\'Courier New\',monospace;">COMMAND CENTER ACTIVE</span></div></div></div>'
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
        threat_html = f'<div style="margin-bottom:12px;border-left:2px solid {severity_color};padding-left:10px;"><div style="font-size:0.75rem;color:#FFFFFF;">[{row["Time"]}] <span style="color:{severity_color};">{row["Source"]}</span></div><div style="font-size:0.8rem;color:#FFFFFF;font-weight:bold;">{row["Vector"]}</div></div>'
        st.markdown(threat_html, unsafe_allow_html=True)


def render_anomaly_map() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// GLOBAL ANOMALY MAP</p>", unsafe_allow_html=True)
    map_html = '<div style="background:#050505;border:1px solid #1A1A1A;padding:25px;border-radius:4px;height:550px;overflow:hidden;"><svg viewBox="0 0 1000 420" style="width:100%;height:100%;"><defs><pattern id="grid-pattern" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="#111" stroke-width="0.5"/></pattern><clipPath id="globe-clip"><circle cx="500" cy="210" r="180" /></clipPath><style>@keyframes globe-spin { 0% { transform: translateX(0); } 100% { transform: translateX(-400px); } } .globe-texture { animation: globe-spin 15s linear infinite; opacity: 0.2; } @keyframes alert-cycle { 0%, 100% { opacity: 0; transform: translateY(10px); } 10%, 40% { opacity: 1; transform: translateY(0); } 50% { opacity: 0; transform: translateY(-10px); } } .map-alert { animation: alert-cycle 8s infinite; }</style></defs><circle cx="500" cy="210" r="181" fill="none" stroke="#222" stroke-width="1" /><g clip-path="url(#globe-clip)"><rect class="globe-texture" width="1400" height="420" fill="url(#grid-pattern)" /></g><line x1="150" y1="150" x2="500" y2="210" class="map-connection" /><line x1="850" y1="120" x2="500" y2="210" class="map-connection" /><line x1="800" y1="350" x2="500" y2="210" class="map-connection" /><circle cx="150" cy="150" r="4" fill="#00D1FF" /><circle cx="150" cy="150" r="4" class="map-node-pulse" style="animation-delay: 0s;" /><text x="140" y="135" fill="#FFFFFF" font-size="10">NODE-US-PROD</text><circle cx="850" cy="120" r="4" fill="#00D1FF" /><circle cx="850" cy="120" r="4" class="map-node-pulse" style="animation-delay: 0.5s;" /><text x="840" y="105" fill="#FFFFFF" font-size="10">NODE-EU-CENTRAL</text><circle cx="800" cy="350" r="4" fill="#00D1FF" /><circle cx="800" cy="350" r="4" class="map-node-pulse" style="animation-delay: 1.2s;" /><text x="790" y="335" fill="#FFFFFF" font-size="10">NODE-AP-SOUTH</text><rect x="485" y="195" width="30" height="30" fill="none" stroke="#FFFFFF" stroke-width="1" /><text x="470" y="245" fill="#FFFFFF" font-size="12" font-weight="bold">SECUREX HUB</text><g class="map-alert"><rect x="650" y="180" width="140" height="45" fill="#0A0A0A" stroke="#00D1FF" stroke-width="0.5" /><text x="660" y="200" fill="#00D1FF" font-size="9" font-weight="bold">THREAT: ISOLATION</text><text x="660" y="215" fill="#FFFFFF" font-size="8">SRC: 10.42.1.204</text></g></svg></div>'
    st.markdown(map_html, unsafe_allow_html=True)


def render_ai_analyst() -> None:
    ai_html = '<div class="ai-analyst-box"><div style="color:#00FF00;font-weight:bold;font-size:0.9rem;margin-bottom:10px;">🤖 AI CHARLIE SOC ANALYST</div><div style="display:flex;gap:30px;"><div style="flex:1;"><p style="color:#FFFFFF;font-size:0.85rem;line-height:1.6;">"Behavioral anomaly detected from Kubernetes worker node 3. Cross-referencing with network logs indicates potential data staging in unauthorized S3 bucket."</p></div><div style="width:200px;border-left:1px solid #1A1A1A;padding-left:20px;"><div style="color:#FFFFFF;font-size:0.65rem;">RISK SCORE</div><div style="color:#00FF00;font-size:1.5rem;font-weight:bold;">82/100</div><div style="margin-top:10px;color:#FFFFFF;font-size:0.7rem;font-weight:bold;">RECOMMENDATION:<br><span style="color:#FFFFFF;font-weight:normal;">Isolate Node 3 & Block egress to bucket audit-exfil-demo.</span></div></div></div></div>'
    st.markdown(ai_html, unsafe_allow_html=True)


def render_pipeline_status() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// AUTOMATION HEALTH</p>", unsafe_allow_html=True)
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        card_html = f'<div class="pipeline-card"><div class="pipeline-name">{row["Pipeline"]}</div><div style="color:#00FF00;font-size:0.75rem;font-weight:bold;margin-top:4px;">● SECURE</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)


def main() -> None:
    # Command Simulation State
    with st.sidebar:
        st.markdown("<p style='color: #777777; font-size: 0.7rem; letter-spacing: 1px;'>// TACTICAL SIMULATION</p>", unsafe_allow_html=True)
        breach_sim = st.toggle("SIMULATE SYSTEM BREACH", value=False)
        
        if st.button("INJECT DETECTION EVENT"):
            new_threat = random.choice([
                {"ID": f"TR-{random.randint(2000, 9000)}", "Severity": random.choice(["High", "Critical", "Medium"]), "Source": random.choice(["Suricata", "CrowdStrike", "Falcon"]), "Vector": random.choice(["Lateral Movement", "Brute Force", "API Abuse"]), "Status": "Investigating"}
            ])
            new_threat["Time"] = datetime.now().strftime("%H:%M:%S")
            # Prepend to keep latest on top
            st.session_state.threat_log = [new_threat] + st.session_state.threat_log[:9]
            st.rerun()

    # Automatic Breach Trigger Logic
    critical_threat_active = any(t.get("Severity") == "Critical" for t in st.session_state.get('threat_log', []))
    active_breach_mode = breach_sim or critical_threat_active

    inject_custom_css(breach_active=active_breach_mode)
    render_header()
    
    col_left, col_center, col_right = st.columns([0.8, 5, 0.8])
    
    with col_left:
        render_active_threats()
        
    with col_center:
        render_anomaly_map()
        
    with col_right:
        render_system_health()
        st.markdown("<br>", unsafe_allow_html=True)
        render_pipeline_status()

    render_ai_analyst()


if __name__ == "__main__":
    main()
