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
            background-color: #00ff00;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            box-shadow: 0 0 8px #00ff00;
            animation: pulse 2s infinite ease-in-out;
        }
        .radar-container {
            position: relative;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, #001a00 0%, #000 70%);
            border: 2px solid #004400;
            border-radius: 50%;
            overflow: hidden;
            margin: 0 auto;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.15);
        }
        .radar-grid {
            position: absolute;
            width: 100%;
            height: 100%;
            background-image: radial-gradient(circle, transparent 30%, rgba(0, 68, 0, 0.2) 31%, transparent 32%), radial-gradient(circle, transparent 60%, rgba(0, 68, 0, 0.2) 61%, transparent 62%);
        }
        .radar-sweep {
            position: absolute;
            width: 100%;
            height: 100%;
            background: conic-gradient(from 0deg, transparent 0%, rgba(0, 255, 0, 0.3) 15%, transparent 30%);
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
            border-left: 4px solid #00ff00;
            margin-bottom: 10px;
        }
        .pipeline-name {
            font-weight: bold;
            font-size: 0.9rem;
            color: #ddd;
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
    <div style="background: rgba(0, 255, 0, 0.1); border: 1px solid #00ff00; padding: 8px 15px; border-radius: 5px;">
        <span class="status-pulse"></span>
        <span style="color: #00ff00; font-weight: bold; font-family: monospace;">SYSTEM: OPERATIONAL</span>
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
            "Medium": "#ffa500",
            "Low": "#00ff00"
        }.get(row["Severity"], "#888")
        
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
    st.subheader("Network Scan")
    st.markdown("""<div class="radar-container">
    <div class="radar-grid"></div>
    <div class="radar-sweep"></div>
    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #00ff0033; font-size: 0.6rem; font-family: monospace;">SCANNING...</div>
</div>""", unsafe_allow_html=True)
    st.caption("Real-time anomaly detection active.")


def render_pipeline_status() -> None:
    st.subheader("Pipeline Status")
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        st.markdown(f"""<div class="pipeline-card">
    <div class="pipeline-name">{row['Pipeline']}</div>
    <div style="color: #00ff00; font-size: 0.8rem;">✅ HEALTHY</div>
</div>""", unsafe_allow_html=True)


def main() -> None:
    inject_custom_css()
    render_header()
    
    col1, col2, col3 = st.columns((2, 1, 1))
    with col1: render_system_health()
    with col2: render_radar()
    with col3: render_pipeline_status()
    
    st.divider()
    render_active_threats()


if __name__ == "__main__":
    main()
