import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Adaptive SOC AI Framework",
    page_icon="🛡️",
    layout="wide",
)


def inject_custom_css() -> None:
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
        @keyframes pulse-crimson {
            0% { transform: scale(0.98); opacity: 0.5; box-shadow: 0 0 4px #FF0055; }
            50% { transform: scale(1.05); opacity: 1; box-shadow: 0 0 14px #FF0055; }
            100% { transform: scale(0.98); opacity: 0.5; box-shadow: 0 0 4px #FF0055; }
        }
        .status-pulse-commander {
            height: 10px;
            width: 10px;
            background-color: #FF0055;
            border-radius: 50%;
            display: inline-block;
            margin-right: 12px;
            animation: pulse-crimson 1.8s infinite ease-in-out;
        }

        /* Global Anomaly Map Animations */
        @keyframes map-pulse {
            0% { r: 4; opacity: 1; }
            100% { r: 12; opacity: 0; }
        }
        .map-node-pulse {
            animation: map-pulse 2s infinite;
            fill: #FF0055;
        }
        @keyframes dash-move {
            to { stroke-dashoffset: -20; }
        }
        .map-connection {
            stroke: #FF0055;
            stroke-width: 1;
            stroke-dasharray: 4, 2;
            animation: dash-move 1s linear infinite;
            opacity: 0.3;
        }

        /* AI Analyst Box */
        .ai-analyst-box {
            background: #0A0A0A;
            border: 1px solid #1A1A1A;
            border-left: 4px solid #FF0055;
            padding: 15px;
            margin-top: 20px;
        }
        
        /* High-Density Command Metric Containers */
        .pipeline-card {
            background: #050505;
            padding: 10px;
            border: 1px solid #1A1A1A;
            border-left: 3px solid #FF0055;
            margin-bottom: 12px;
        }
        .pipeline-name {
            font-weight: bold;
            font-size: 0.85rem;
            color: #FFFFFF;
            letter-spacing: 1px;
        }
        .metric-value {
            color: #FF0055;
            font-weight: bold;
        }
        .secondary-text {
            color: #777777;
            font-size: 0.75rem;
        }
        
        /* Tactical Metric Overrides */
        [data-testid="stMetric"] {
            background-color: #000000 !important;
            border: 1px solid #222222 !important;
            padding: 15px !important;
        }
        [data-testid="stMetricValue"] > div {
            color: #FF0055 !important;
            font-family: 'Courier New', monospace !important;
        }
        [data-testid="stMetricLabel"] > div {
            color: #FFFFFF !important;
        }
        </style>
    """, unsafe_allow_html=True)


def get_system_health_data() -> dict:
    return {"cpu_percent": 42, "memory_percent": 68}


def get_active_threats_data() -> pd.DataFrame:
    return pd.DataFrame([
        {"Time": "18:04:22", "ID": "TR-1081", "Severity": "Critical", "Source": "Suricata", "Vector": "Exfiltration", "Status": "Intercepted"},
        {"Time": "18:04:25", "ID": "TR-1082", "Severity": "High", "Source": "Core Defense", "Vector": "Privilege Esc", "Status": "Isolating"},
        {"Time": "18:04:31", "ID": "TR-1083", "Severity": "Medium", "Source": "Kube-Linter", "Vector": "Misconfig", "Status": "Triaged"},
        {"Time": "18:04:36", "ID": "TR-1088", "Severity": "Low", "Source": "GuardDuty", "Vector": "Port Scan", "Status": "Logged"}
    ])


def get_pipeline_status_data() -> pd.DataFrame:
    return pd.DataFrame([
        {"Pipeline": "Terraform Engine", "Status": "ACTIVE"},
        {"Pipeline": "Ansible Automation", "Status": "ACTIVE"},
        {"Pipeline": "Docker Runtime", "Status": "ACTIVE"},
        {"Pipeline": "Kubernetes Cluster", "Status": "ACTIVE"}
    ])


def render_header() -> None:
    st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 30px; border-bottom: 1px solid #1A1A1A; padding-bottom: 20px;">
    <div>
        <h1 style="margin: 0; font-family: 'Courier New', monospace; font-size: 1.6rem; font-weight: 900; letter-spacing: 4px; color: #FFFFFF;">SECUREX COMMAND</h1>
        <p style="color: #777777; margin: 5px 0 0 0; font-size: 0.75rem; letter-spacing: 1px;">[ SYSTEM INFRASTRUCTURE MONITORING V1.0 ]</p>
    </div>
    <div style="display: flex; gap: 40px; align-items: center;">
        <div style="text-align: right;">
            <div style="color: #777777; font-size: 0.65rem; letter-spacing: 1px;">THREATS TODAY</div>
            <div style="color: #FF0055; font-weight: bold; font-size: 1.2rem;">17</div>
        </div>
        <div style="text-align: right;">
            <div class="metric-label">ASSETS MONITORED</div>
            <div style="color: #FFFFFF; font-weight: bold; font-size: 1.2rem;">2,491</div>
        </div>
        <div style="background: #000000; border: 1px solid #FF0055; padding: 8px 15px;">
            <span class="status-pulse-commander"></span>
            <span style="color: #FF0055; font-weight: bold; font-size: 0.8rem; letter-spacing: 2px; font-family: 'Courier New', monospace;">COMMAND CENTER ACTIVE</span>
        </div>
    </div>
</div>
    """, unsafe_allow_html=True)


def render_system_health() -> None:
    health = get_system_health_data()
    st.markdown("<p style='color: #777777; margin: 0 0 10px 0; font-size: 0.7rem;'>// RESOURCE ALLOCATION</p>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("CPU Usage", f"{health['cpu_percent']}%")
    col2.metric("Memory", f"{health['memory_percent']}%")


def render_active_threats() -> None:
    threats = get_active_threats_data()
    st.markdown("<p style='color: #777777; margin: 0 0 10px 0; font-size: 0.7rem;'>// LIVE THREAT FEED</p>", unsafe_allow_html=True)
    for _, row in threats.iterrows():
        severity_color = {"Critical": "#FF0055", "High": "#FFFFFF", "Medium": "#777777", "Low": "#444444"}.get(row["Severity"], "#222222")
        threat_html = f'<div style="margin-bottom:12px;border-left:2px solid {severity_color};padding-left:10px;"><div style="font-size:0.75rem;color:#777777;">[{row["Time"]}] <span style="color:{severity_color};">{row["Source"]}</span></div><div style="font-size:0.8rem;color:#FFFFFF;font-weight:bold;">{row["Vector"]}</div></div>'
        st.markdown(threat_html, unsafe_allow_html=True)


def render_anomaly_map() -> None:
    st.markdown("<p style='color: #777777; margin: 0 0 10px 0; font-size: 0.7rem;'>// GLOBAL ANOMALY MAP</p>", unsafe_allow_html=True)
    map_html = '<div style="background:#050505;border:1px solid #1A1A1A;padding:20px;border-radius:4px;"><svg viewBox="0 0 800 350" style="width:100%;"><line x1="150" y1="100" x2="400" y2="180" class="map-connection" /><line x1="600" y1="80" x2="400" y2="180" class="map-connection" /><line x1="650" y1="280" x2="400" y2="180" class="map-connection" /><circle cx="150" cy="100" r="4" fill="#FF0055" /><circle cx="150" cy="100" r="4" class="map-node-pulse" /><text x="140" y="85" fill="#777777" font-size="10">USA-WEST-01</text><circle cx="600" cy="80" r="4" fill="#FF0055" /><circle cx="600" cy="80" r="4" class="map-node-pulse" /><text x="590" y="65" fill="#777777" font-size="10">EU-CENTRAL-1</text><circle cx="650" cy="280" r="4" fill="#FF0055" /><circle cx="650" cy="280" r="4" class="map-node-pulse" /><text x="640" y="265" fill="#777777" font-size="10">APAC-SOUTH-02</text><rect x="385" y="165" width="30" height="30" fill="none" stroke="#FFFFFF" stroke-width="1" /><text x="380" y="215" fill="#FFFFFF" font-size="12" font-weight="bold">SOC CORE</text><rect x="520" y="150" width="120" height="40" fill="#0A0A0A" stroke="#FF0055" stroke-width="0.5" /><text x="530" y="165" fill="#FF0055" font-size="9" font-weight="bold">ANOMALY DETECTED</text><text x="530" y="180" fill="#777777" font-size="8">IP: 192.168.1.42</text></svg></div>'
    st.markdown(map_html, unsafe_allow_html=True)


def render_ai_analyst() -> None:
    ai_html = '<div class="ai-analyst-box"><div style="color:#FF0055;font-weight:bold;font-size:0.9rem;margin-bottom:10px;">🤖 AI CHARLIE SOC ANALYST</div><div style="display:flex;gap:30px;"><div style="flex:1;"><p style="color:#FFFFFF;font-size:0.85rem;line-height:1.6;">"Behavioral anomaly detected from Kubernetes worker node 3. Cross-referencing with network logs indicates potential data staging in unauthorized S3 bucket."</p></div><div style="width:200px;border-left:1px solid #1A1A1A;padding-left:20px;"><div style="color:#777777;font-size:0.65rem;">RISK SCORE</div><div style="color:#FF0055;font-size:1.5rem;font-weight:bold;">82/100</div><div style="margin-top:10px;color:#FFFFFF;font-size:0.7rem;font-weight:bold;">RECOMMENDATION:<br><span style="color:#777777;font-weight:normal;">Isolate Node 3 & Block egress to bucket audit-exfil-demo.</span></div></div></div></div>'
    st.markdown(ai_html, unsafe_allow_html=True)


def render_pipeline_status() -> None:
    st.markdown("<p style='color: #777777; margin: 0 0 10px 0; font-size: 0.7rem;'>// AUTOMATION HEALTH</p>", unsafe_allow_html=True)
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        card_html = f'<div class="pipeline-card"><div class="pipeline-name">{row["Pipeline"]}</div><div style="color:#FF0055;font-size:0.75rem;font-weight:bold;margin-top:4px;">● SECURE</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)


def main() -> None:
    inject_custom_css()
    render_header()
    
    col_left, col_center, col_right = st.columns([1, 2.5, 1])
    
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
