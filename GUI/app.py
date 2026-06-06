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
        
        /* Advanced Cyber Scanner Graphic */
        .radar-box {
            position: relative;
            width: 160px;
            height: 160px;
            background: radial-gradient(circle, #150005 0%, #000000 85%);
            border: 1px solid #222222;
            border-radius: 50%;
            overflow: hidden;
            margin: 0 auto;
        }
        .radar-grid-lines {
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle, transparent 35%, rgba(51, 51, 51, 0.3) 36%, transparent 37%),
                radial-gradient(circle, transparent 65%, rgba(51, 51, 51, 0.3) 66%, transparent 67%);
        }
        .radar-sweep-line {
            position: absolute;
            width: 100%;
            height: 100%;
            background: conic-gradient(from 0deg, transparent 45%, rgba(255, 0, 85, 0.3) 100%);
            animation: sweep-rotate 2.5s linear infinite;
        }
        @keyframes sweep-rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        /* High-Density Command Metric Containers */
        .pipeline-card {
            background: #050505;
            padding: 14px;
            border: 1px solid #222222;
            border-left: 4px solid #FF0055;
            margin-bottom: 12px;
        }
        .pipeline-name {
            font-weight: bold;
            font-size: 0.85rem;
            color: #FFFFFF;
            letter-spacing: 1px;
        }
        </style>
    """, unsafe_allow_html=True)


def get_system_health_data() -> dict:
    return {"cpu_percent": 42, "memory_percent": 68}


def get_active_threats_data() -> pd.DataFrame:
    return pd.DataFrame([
        {"ID": "TR-1081", "Severity": "Critical", "Source": "Suricata", "Vector": "Exfiltration", "Status": "Intercepted"},
        {"ID": "TR-1082", "Severity": "High", "Source": "Core Defense", "Vector": "Privilege Esc", "Status": "Isolating"},
        {"ID": "TR-1083", "Severity": "Medium", "Source": "Kube-Linter", "Vector": "Misconfig", "Status": "Triaged"}
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
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 35px; border-bottom: 1px solid #111111; padding-bottom: 20px;">
    <div>
        <h1 style="margin: 0; font-size: 1.6rem; font-weight: 900; letter-spacing: 3px; color: #FFFFFF;">SECUREX // ADAPTIVE SOC</h1>
        <p style="color: #777777; margin: 5px 0 0 0; font-size: 0.8rem; letter-spacing: 1px;">[ DEFEND • DETECT • RESPOND // WORKSPACE HEAD: COMMANDER ]</p>
    </div>
    <div style="background: #000000; border: 1px solid #FF0055; padding: 10px 18px;">
        <span class="status-pulse-commander"></span>
        <span style="color: #FF0055; font-weight: bold; font-size: 0.8rem; letter-spacing: 2px;">DEFCON ACTIVE</span>
    </div>
</div>
    """, unsafe_allow_html=True)


def render_system_health() -> None:
    health = get_system_health_data()
    st.markdown("<p style='color: #444444; margin: 0 0 4px 0; font-size: 0.75rem;'>// CORE SYSTEM RESOURCES</p>", unsafe_allow_html=True)
    st.subheader("System Health")
    col1, col2 = st.columns(2)
    col1.metric("CPU ALLOCATION", f"{health['cpu_percent']}%")
    col2.metric("MEMORY POOLS", f"{health['memory_percent']}%")


def render_active_threats() -> None:
    threats = get_active_threats_data()
    st.markdown("<p style='color: #444444; margin: 0 0 4px 0; font-size: 0.75rem;'>// VECTOR STREAM AUDIT LOGS</p>", unsafe_allow_html=True)
    st.subheader("Live Command Threat Stream")
    for _, row in threats.iterrows():
        severity_color = {"Critical": "#FF0055", "High": "#FFFFFF", "Medium": "#666666"}.get(row["Severity"], "#222222")
        
        st.markdown(f"""<div style="
            background: #050505;
            padding: 12px 16px;
            margin-bottom: 10px;
            border: 1px solid #222222;
            border-left: 4px solid {severity_color};
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <span style="color: {severity_color}; font-weight: bold; letter-spacing: 1px;">[{row['Severity'].upper()}]</span>
                <span style="color: #FFFFFF; margin-left: 15px; font-weight: bold;">{row['Vector']}</span>
                <br>
                <span style="color: #555555; font-size: 0.75rem;">Source: {row['Source']} | Strategy: {row['Status']}</span>
            </div>
            <div style="color: #FF0055; font-size: 0.8rem; font-weight: bold;">{row['ID']}</div>
        </div>""", unsafe_allow_html=True)


def render_radar() -> None:
    st.markdown("<p style='color: #444444; margin: 0 0 4px 0; font-size: 0.75rem;'>// ANOMALY SPATIAL DETECTION</p>", unsafe_allow_html=True)
    st.subheader("Network Scan Mesh")
    st.markdown("""<div class="radar-box">
    <div class="radar-grid-lines"></div>
    <div class="radar-sweep-line"></div>
    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #FF0055AA; font-size: 0.6rem; font-weight: bold; letter-spacing: 1px;">SCAN ACTIVE</div>
</div>
    """, unsafe_allow_html=True)


def render_pipeline_status() -> None:
    st.markdown("<p style='color: #444444; margin: 0 0 4px 0; font-size: 0.75rem;'>// CI ENGINE METRICS</p>", unsafe_allow_html=True)
    st.subheader("Pipeline Automation")
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        card_html = f'<div class="pipeline-card"><div class="pipeline-name">{row["Pipeline"]}</div><div style="color:#FF0055;font-size:0.75rem;font-weight:bold;margin-top:4px;">>>> SECURE OPERATIONAL</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)


def main() -> None:
    inject_custom_css()
    render_header()
    
    col1, col2, col3 = st.columns([1.8, 1.1, 1.1])
    with col1:
        render_system_health()
    with col2:
        render_radar()
    with col3:
        render_pipeline_status()
    
    st.markdown("<br><hr style='border: 0; border-top: 1px solid #222222;'/>", unsafe_allow_html=True)
    render_active_threats()


if __name__ == "__main__":
    main()
