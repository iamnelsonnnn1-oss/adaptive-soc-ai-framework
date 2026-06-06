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
        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.7; }
            50% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.7; }
        }
        .status-pulse {
            height: 10px;
            width: 10px;
            background-color: #ff0000;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            box-shadow: 0 0 8px #ff0000;
            animation: pulse 2s infinite ease-in-out;
        }
        .radar-container {
            position: relative;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, #1a0000 0%, #000 70%);
            border: 2px solid #440000;
            border-radius: 50%;
            overflow: hidden;
            margin: 0 auto;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.15);
        }
        .radar-grid {
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: radial-gradient(circle, transparent 30%, rgba(68, 0, 0, 0.2) 31%, transparent 32%), radial-gradient(circle, transparent 60%, rgba(68, 0, 0, 0.2) 61%, transparent 62%);
        }
        .radar-sweep {
            position: absolute;
            width: 100%;
            height: 100%;
            background: conic-gradient(from 0deg, transparent 0%, rgba(255, 0, 0, 0.3) 15%, transparent 30%);
            animation: rotate 4s linear infinite;
        }
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .pipeline-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #ff0000;
            margin-bottom: 10px;
        }
        .pipeline-name {
            font-weight: bold;
            font-size: 0.9rem;
            color: #ddd;
        }
        .anomaly-map-container {
            width: 100%;
            height: 300px;
            background-color: #050505;
            border: 1px solid #333;
            border-radius: 10px;
            position: relative;
            overflow: hidden;
            background-image: 
                linear-gradient(rgba(255, 0, 0, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 0, 0, 0.05) 1px, transparent 1px);
            background-size: 30px 30px;
        }
        .map-hotspot {
            position: absolute;
            width: 12px;
            height: 12px;
            background-color: #ff0000;
            border-radius: 50%;
            box-shadow: 0 0 15px #ff0000;
            animation: pulse 1.5s infinite;
        }
        </style>
    """, unsafe_allow_html=True)


def get_system_health_data() -> dict:
    # Placeholder for future Docker service API integration.
    return {
        "cpu_percent": 42,
        "memory_percent": 68,
    }


def get_active_threats_data() -> pd.DataFrame:
    # Placeholder for future Docker service API integration.
    return pd.DataFrame(
        [
            {
                "Threat ID": "evt-1001",
                "Severity": "Medium",
                "Source": "Suricata",
                "Category": "Network Anomaly",
                "Status": "Triaged",
            },
            {
                "Threat ID": "evt-1002",
                "Severity": "High",
                "Source": "Darktrace",
                "Category": "Behavioral Anomaly",
                "Status": "Investigating",
            },
            {
                "Threat ID": "evt-1003",
                "Severity": "Low",
                "Source": "LimaCharlie",
                "Category": "Endpoint Observation",
                "Status": "Open",
            },
        ]
    )


def get_pipeline_status_data() -> pd.DataFrame:
    # Placeholder for future Docker service API integration.
    return pd.DataFrame(
        [
            {"Pipeline": "Terraform CI", "Status": "Pass"},
            {"Pipeline": "Ansible CI", "Status": "Pass"},
            {"Pipeline": "Docker CI", "Status": "Pass"},
            {"Pipeline": "Kubernetes CI", "Status": "Pass"},
        ]
    )


def render_header() -> None:
    st.markdown("""<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
    <div>
        <h1 style="margin: 0;">🛡️ Adaptive SOC AI Framework</h1>
        <p style="color: #888; margin: 0;">Infrastructure, Automation, and Threat Visibility</p>
    </div>
    <div style="background: rgba(255, 0, 0, 0.1); border: 1px solid #ff0000; padding: 8px 15px; border-radius: 5px;">
        <span class="status-pulse"></span>
        <span style="color: #ff0000; font-weight: bold; font-family: monospace;">SYSTEM: THREAT MONITORING ACTIVE</span>
    </div>
</div>""", unsafe_allow_html=True)


def render_system_health() -> None:
    health = get_system_health_data()
    st.subheader("System Health")
    col1, col2 = st.columns(2)
    col1.metric("CPU Usage", f"{health['cpu_percent']}%")
    col2.metric("Memory Usage", f"{health['memory_percent']}%")


def render_active_threats() -> None:
    threats = get_active_threats_data()
    st.subheader("Live Threat Feed")
    for _, row in threats.iterrows():
        severity_color = {
            "High": "#ff4b4b",
            "Medium": "#ffffff",
            "Low": "#ffffff"
        }.get(row["Severity"], "#ffffff")
        
        st.markdown(f"""<div style="
            font-family: 'Courier New', monospace;
            background: rgba(255, 255, 255, 0.05);
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 8px;
            border-left: 4px solid {severity_color};
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div>
                <span style="color: {severity_color}; font-weight: bold;">[{row['Severity'].upper()}]</span>
                <span style="color: #fff; margin-left: 10px;">{row['Category']}</span>
                <br>
                <span style="color: #888; font-size: 0.8rem;">Source: {row['Source']} | Status: {row['Status']}</span>
            </div>
            <div style="color: #444; font-size: 0.7rem;">{row['Threat ID']}</div>
        </div>""", unsafe_allow_html=True)


def render_radar() -> None:
    st.subheader("Autonomous AI Threat Topology")
    st.markdown("""<div class="radar-container" style="width: 220px; height: 220px; border: 2px dashed #ff0000; background: radial-gradient(circle, #1a0000 10%, #000000 90%); position: relative;">
    <div class="radar-grid"></div>
    <div class="radar-sweep" style="animation: rotate 3s linear infinite; background: conic-gradient(from 0deg, transparent 60%, rgba(255, 0, 0, 0.4) 100%);"></div>
    <div style="position: absolute; top: 35%; left: 60%; width: 8px; height: 8px; background-color: #ff4b4b; border-radius: 50%; box-shadow: 0 0 12px #ff4b4b;"></div>
    <div style="position: absolute; top: 70%; left: 30%; width: 6px; height: 6px; background-color: #ffffff; border-radius: 50%; box-shadow: 0 0 8px #ffffff;"></div>
    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #ff000088; font-size: 0.7rem; font-family: monospace; font-weight: bold; letter-spacing: 1px;">ANOMALY TRACKING</div>
</div>""", unsafe_allow_html=True)
    st.caption("Self-learning AI models mapping device behavior strings across cluster nodes.")


def render_anomaly_map() -> None:
    st.subheader("Global SIEM Anomaly Map")
    st.markdown("""<div class="anomaly-map-container">
    <div class="map-hotspot" style="top: 20%; left: 30%;"></div>
    <div class="map-hotspot" style="top: 45%; left: 75%;"></div>
    <div class="map-hotspot" style="top: 60%; left: 15%;"></div>
    <div class="map-hotspot" style="top: 80%; left: 55%;"></div>
    <div style="position: absolute; bottom: 10px; right: 15px; color: #ff0000; font-family: monospace; font-size: 0.7rem; background: rgba(0,0,0,0.7); padding: 5px;">
        LIVE INGRESS ANOMALIES DETECTED
    </div>
</div>""", unsafe_allow_html=True)


def render_pipeline_status() -> None:
    st.subheader("Pipeline Status")
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        st.markdown(f"""<div class="pipeline-card">
    <div class="pipeline-name">{row['Pipeline']}</div>
    <div style="color: #ff0000; font-size: 0.8rem;">✅ HEALTHY</div>
</div>""", unsafe_allow_html=True)


def main() -> None:
    inject_custom_css()
    render_header()
    
    # Large Map across the top section
    render_anomaly_map()
    st.divider()

    col1, col2, col3 = st.columns((2, 1, 1))
    with col1: render_system_health()
    with col2: render_radar()
    with col3: render_pipeline_status()
    
    st.divider()
    render_active_threats()


if __name__ == "__main__":
    main()
