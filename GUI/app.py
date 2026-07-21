import json
import os
import random
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="SecureX Command SOC Simulator", page_icon="🛡️", layout="wide")


SEVERITY_SCORE = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
REGIONS = [
    ("Frankfurt", 50.1109, 8.6821),
    ("Dublin", 53.3498, -6.2603),
    ("Amsterdam", 52.3676, 4.9041),
    ("Paris", 48.8566, 2.3522),
    ("Madrid", 40.4168, -3.7038),
    ("Warsaw", 52.2297, 21.0122),
]
SOURCES = ["Suricata", "Darktrace", "LimaCharlie", "Chronicle", "Elastic"]
VECTORS = [
    "Credential Stuffing Burst",
    "Ransomware Beacon Activity",
    "Lateral Movement via SMB",
    "Suspicious OAuth Token Reuse",
    "DNS Tunneling Pattern",
    "Privilege Escalation Attempt",
]
MITRE = ["T1110", "T1486", "T1021", "T1528", "T1071", "T1068"]
STATUSES = ["Open", "Investigating", "Contained", "Closed"]
TRIAGE_ACTIONS = ["Isolate Host", "Reset Credentials", "Block IOC", "Escalate to IR"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def generate_incident(index_seed: int = 0) -> dict:
    city, lat, lon = random.choice(REGIONS)
    sev = random.choices(["Critical", "High", "Medium", "Low"], weights=[1, 2, 3, 4], k=1)[0]
    vector_index = random.randrange(len(VECTORS))
    return {
        "ID": f"INC-{int(datetime.now(timezone.utc).timestamp())}-{index_seed}",
        "Time": utc_now(),
        "Severity": sev,
        "Source": random.choice(SOURCES),
        "Region": city,
        "lat": lat + random.uniform(-0.4, 0.4),
        "lon": lon + random.uniform(-0.4, 0.4),
        "Vector": VECTORS[vector_index],
        "MITRE": MITRE[vector_index],
        "Status": random.choice(STATUSES[:2]),
        "AnalystNote": "Pending triage.",
    }


def init_state() -> None:
    if "incidents" not in st.session_state:
        st.session_state.incidents = [generate_incident(i) for i in range(6)]
    if "selected_id" not in st.session_state:
        st.session_state.selected_id = st.session_state.incidents[0]["ID"]
    if "activity_log" not in st.session_state:
        st.session_state.activity_log = []
    if "auto_sim" not in st.session_state:
        st.session_state.auto_sim = False


def append_log(message: str) -> None:
    st.session_state.activity_log.insert(0, f"[{utc_now()}] {message}")
    st.session_state.activity_log = st.session_state.activity_log[:40]


def inject_incident() -> None:
    incident = generate_incident(len(st.session_state.incidents) + 1)
    st.session_state.incidents.insert(0, incident)
    st.session_state.selected_id = incident["ID"]
    append_log(f"Injected simulated incident {incident['ID']} ({incident['Severity']}).")


def get_selected_incident() -> dict | None:
    selected = next(
        (incident for incident in st.session_state.incidents if incident["ID"] == st.session_state.selected_id),
        None,
    )
    if selected:
        return selected
    if not st.session_state.incidents:
        return None
    st.session_state.selected_id = st.session_state.incidents[0]["ID"]
    return st.session_state.incidents[0]


def update_incident(selected_id: str, status: str, action: str, note: str) -> None:
    for incident in st.session_state.incidents:
        if incident["ID"] == selected_id:
            incident["Status"] = status
            incident["AnalystNote"] = note.strip() or incident["AnalystNote"]
            append_log(f"{action} executed on {selected_id}; status -> {status}.")
            break


def render_top_metrics(df: pd.DataFrame) -> None:
    total = len(df)
    open_count = int((df["Status"] != "Closed").sum()) if not df.empty else 0
    critical = int((df["Severity"] == "Critical").sum()) if not df.empty else 0
    contained = int((df["Status"] == "Contained").sum()) if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("INCIDENTS", total)
    c2.metric("OPEN", open_count)
    c3.metric("CRITICAL", critical)
    c4.metric("CONTAINED", contained)


def render_map(df: pd.DataFrame) -> None:
    st.subheader("Threat Geomap")
    if df.empty:
        st.info("No incident data available.")
        return

    plot_df = df.copy()
    plot_df["SeverityScore"] = plot_df["Severity"].map(SEVERITY_SCORE)
    fig = px.scatter_geo(
        plot_df,
        lat="lat",
        lon="lon",
        color="Severity",
        size="SeverityScore",
        hover_name="ID",
        hover_data={"Region": True, "Vector": True, "Status": True, "lat": False, "lon": False},
        projection="natural earth",
        title="Simulated Incident Distribution",
    )
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, use_container_width=True)


def render_queue(df: pd.DataFrame) -> None:
    st.subheader("Live Triage Queue")
    if df.empty:
        st.info("Queue is empty.")
        return
    queue = df[["ID", "Time", "Severity", "Source", "Region", "Vector", "Status"]]
    st.dataframe(queue, use_container_width=True, hide_index=True)


def render_sidebar_controls(df: pd.DataFrame) -> None:
    with st.sidebar:
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=160)

        st.header("Simulator Control")
        st.caption("SecureX Command SOC Simulator")

        if st.button("Inject Simulated Attack", use_container_width=True):
            inject_incident()
            st.rerun()

        st.session_state.auto_sim = st.toggle("Auto simulation mode", value=st.session_state.auto_sim)
        if st.session_state.auto_sim and st.button("Run one auto-sim tick", use_container_width=True):
            inject_incident()
            st.rerun()

        options = list(df["ID"]) if not df.empty else []
        if options:
            current_idx = options.index(st.session_state.selected_id) if st.session_state.selected_id in options else 0
            st.session_state.selected_id = st.selectbox("Focus incident", options, index=current_idx)
        else:
            st.info("No active incident to select.")


def render_triage_panel(selected: dict | None) -> None:
    st.subheader("Incident Triage Console")
    if not selected:
        st.info("No incident selected.")
        return

    st.markdown(
        f"**{selected['ID']}**  \n"
        f"Severity: **{selected['Severity']}** | Source: **{selected['Source']}** | MITRE: **{selected['MITRE']}**"
    )
    st.write(f"Vector: {selected['Vector']}")

    with st.form("triage_form"):
        action = st.selectbox("Action", TRIAGE_ACTIONS)
        status = st.selectbox("Status", STATUSES, index=STATUSES.index(selected["Status"]) if selected["Status"] in STATUSES else 0)
        note = st.text_area("Analyst note", value=selected.get("AnalystNote", ""), height=90)
        submitted = st.form_submit_button("Apply Triage Update", use_container_width=True)

    if submitted:
        update_incident(selected["ID"], status, action, note)
        st.success(f"Updated {selected['ID']}")
        st.rerun()

    report_payload = {
        "generated_at": utc_now(),
        "incident": selected,
        "queue_size": len(st.session_state.incidents),
        "activity_log": st.session_state.activity_log[:15],
    }
    st.download_button(
        "Download Incident Report (JSON)",
        data=json.dumps(report_payload, indent=2),
        file_name=f"{selected['ID']}-report.json",
        mime="application/json",
        use_container_width=True,
    )


def render_activity_log() -> None:
    st.subheader("Operations Log")
    if not st.session_state.activity_log:
        st.info("No operations logged yet.")
        return
    for item in st.session_state.activity_log[:15]:
        st.code(item)


def main() -> None:
    init_state()
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=220)

    st.title("SecureX Command SOC Simulator")
    st.caption("Interactive SOC/SIEM simulator for live triage and incident reporting.")

    df = pd.DataFrame(st.session_state.incidents)
    render_sidebar_controls(df)
    render_top_metrics(df)

    left, right = st.columns([1.8, 1.1])
    with left:
        render_map(df)
        render_queue(df)
    with right:
        render_triage_panel(get_selected_incident())
        st.divider()
        render_activity_log()


if __name__ == "__main__":
    main()
