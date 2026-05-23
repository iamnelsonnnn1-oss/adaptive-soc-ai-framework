import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Adaptive SOC AI Framework",
    page_icon="🛡️",
    layout="wide",
)


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
        ]
    )


def render_header() -> None:
    st.title("Adaptive SOC AI Framework")
    st.caption("Demo dashboard for infrastructure, automation, and runtime visibility.")


def render_system_health() -> None:
    health = get_system_health_data()
    st.subheader("System Health")
    col1, col2 = st.columns(2)
    col1.metric("CPU Usage", f"{health['cpu_percent']}%")
    col2.metric("Memory Usage", f"{health['memory_percent']}%")


def render_active_threats() -> None:
    threats = get_active_threats_data()
    st.subheader("Active Threats")
    st.dataframe(threats, use_container_width=True, hide_index=True)


def render_pipeline_status() -> None:
    pipelines = get_pipeline_status_data().copy()
    pipelines["Status Indicator"] = pipelines["Status"].map(
        {"Pass": "✅ Pass", "Fail": "❌ Fail"}
    )
    st.subheader("Pipeline Status")
    st.dataframe(
        pipelines[["Pipeline", "Status Indicator"]],
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    render_header()
    top_left, top_right = st.columns((2, 1))

    with top_left:
        render_system_health()

    with top_right:
        render_pipeline_status()

    st.divider()
    render_active_threats()


if __name__ == "__main__":
    main()
