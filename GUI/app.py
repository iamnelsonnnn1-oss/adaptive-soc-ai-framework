import json
import os
import random
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="SecureX Command SOC Simulator", page_icon="🛡️", layout="wide")


TACTICS = [
    ("TA0001", "Initial Access"),
    ("TA0006", "Credential Access"),
    ("TA0004", "Privilege Escalation"),
    ("TA0008", "Lateral Movement"),
    ("TA0009", "Collection"),
    ("TA0010", "Exfiltration"),
    ("TA0011", "Command & Control"),
    ("TA0040", "Impact"),
]
TACTIC_ORDER = {name: index for index, (_, name) in enumerate(TACTICS)}
TACTIC_TO_TECHNIQUES = {
    "Initial Access": ["T1566 Phishing", "T1190 Public App", "T1133 External Remote Services"],
    "Credential Access": ["T1110 Brute Force", "T1003 OS Credential Dumping", "T1555 Credentials from Password Stores"],
    "Privilege Escalation": ["T1068 Exploitation for Privilege Escalation", "T1134 Access Token Manipulation", "T1548 Abuse Elevation Control"],
    "Lateral Movement": ["T1021 Remote Services", "T1210 Exploitation of Remote Services", "T1570 Lateral Tool Transfer"],
    "Collection": ["T1056 Input Capture", "T1005 Data from Local System", "T1114 Email Collection"],
    "Exfiltration": ["T1041 Exfiltration Over C2 Channel", "T1567 Exfiltration to Cloud Storage", "T1020 Automated Exfiltration"],
    "Command & Control": ["T1071 Application Layer Protocol", "T1105 Ingress Tool Transfer", "T1095 Non-Application Layer Protocol"],
    "Impact": ["T1486 Data Encrypted for Impact", "T1499 Endpoint DoS", "T1565 Data Manipulation"],
}
SEVERITY_SCORE = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
SEVERITY_COLOR = {
    "critical": "#ef4444",
    "high": "#f97316",
    "medium": "#f59e0b",
    "low": "#38bdf8",
    "info": "#64748b",
}
SEVERITY_WEIGHT_CHOICES = [("critical", 10), ("high", 8), ("medium", 6), ("low", 4), ("info", 2)]
STATUS_OPTIONS = ["new", "triaging", "investigating", "remediated", "closed"]
STACK = [
    ("Tines", "SOAR"),
    ("LimaCharlie", "EDR/XDR"),
    ("Cybereason", "EDR/XDR"),
    ("Darktrace", "NDR/AI"),
    ("Suricata", "IDS/IPS"),
    ("ELK Stack", "SIEM"),
    ("Google SecOps", "SIEM"),
]


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #020617; color: #e2e8f0; }
        .sticky-header {
          position: sticky; top: 0; z-index: 99;
          background: rgba(2, 6, 23, 0.95);
          border: 1px solid rgba(56, 189, 248, 0.25);
          border-radius: 10px; padding: 10px 14px; margin-bottom: 14px;
          backdrop-filter: blur(3px);
        }
        .chip { display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase; }
        .feed-card {
          border:1px solid rgba(148,163,184,.28);
          border-left:4px solid #38bdf8;
          border-radius:8px; padding:8px 10px; margin-bottom:8px; background: rgba(15, 23, 42, 0.65);
        }
        .legend { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:8px; }
        .legend-pill {
          border:1px solid rgba(148,163,184,.35); border-radius:999px; padding:2px 8px; font-size:11px;
        }
        .matrix-grid { display:grid; grid-template-columns: 200px repeat(8, 1fr); gap:6px; margin-top:8px; }
        .matrix-head, .matrix-label {
          font-size:11px; font-weight:700; border:1px solid rgba(148,163,184,.35); border-radius:6px;
          padding:6px; background: rgba(15,23,42,.6);
        }
        .matrix-cell {
          position:relative; border-radius:6px; border:1px solid rgba(148,163,184,.35);
          padding:8px 6px; text-align:center; font-size:12px; font-weight:700;
          transition: transform .15s ease-in-out;
        }
        .matrix-cell:hover { transform: scale(1.06); }
        .ok-dot {
          position:absolute; top:4px; right:6px; width:8px; height:8px;
          border-radius:999px; background:#22c55e; box-shadow:0 0 8px #22c55e;
        }
        .stack-card {
          border:1px solid rgba(148,163,184,.3); border-radius:8px;
          background: rgba(15,23,42,.7); padding:10px; min-height:74px;
        }
        .status-dot {
          display:inline-block; width:8px; height:8px; border-radius:999px;
          background:#22c55e; margin-right:6px; box-shadow:0 0 8px #22c55e;
        }
        .stTabs [data-baseweb="tab-list"] {
          gap: 10px;
          margin-bottom: 8px;
        }
        .stTabs [data-baseweb="tab"] {
          border-radius: 8px;
          border: 1px solid rgba(148,163,184,.35);
          background: rgba(15,23,42,.65);
          padding: 8px 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_threats() -> list[dict]:
    seeds = [
        ("Credential stuffing burst against SSO portal", "critical", "new", "credential_theft", "185.217.0.14", "auth-gateway-01", "Credential Access", 94, "detect", "Suricata"),
        ("Ransomware encryption beacon chain detected", "critical", "investigating", "malware", "45.134.22.91", "finance-sql-02", "Impact", 96, "respond", "Darktrace"),
        ("Suspicious admin token replay", "high", "triaging", "privilege_escalation", "91.240.118.77", "iam-control-plane", "Privilege Escalation", 88, "protect", "Google SecOps"),
        ("Lateral movement over SMB from workstation", "high", "new", "lateral_movement", "10.18.44.12", "hr-files-03", "Lateral Movement", 87, "detect", "LimaCharlie"),
        ("Potential data staging in temp cloud bucket", "medium", "new", "data_exfiltration", "172.16.30.7", "object-store-eu", "Collection", 76, "identify", "ELK Stack"),
        ("DNS tunneling candidate to rare domain", "medium", "investigating", "zero_day", "203.0.113.34", "proxy-egress-01", "Command & Control", 81, "respond", "Suricata"),
        ("OAuth phishing lure clicked by sales user", "high", "remediated", "phishing", "66.102.8.1", "sales-laptop-22", "Initial Access", 85, "recover", "Google SecOps"),
        ("Anomalous outbound transfer spike", "low", "triaging", "insider_threat", "10.22.11.31", "legal-share-01", "Exfiltration", 69, "detect", "Darktrace"),
        ("DDoS probing pattern on edge API", "low", "new", "ddos", "198.51.100.8", "edge-api-03", "Impact", 66, "protect", "ELK Stack"),
        ("Isolation Forest anomaly on service account behavior (zero-day candidate)", "medium", "new", "zero_day", "10.44.5.90", "svc-kube-bot", "Command & Control", 83, "identify", "Cybereason"),
    ]
    base = datetime.now(timezone.utc)
    out = []
    for idx, row in enumerate(seeds, start=1):
        title, severity, status, category, src, target, tactic, confidence, nist, tool = row
        out.append(
            {
                "id": f"THR-{idx:04d}",
                "title": title,
                "description": f"{title}. Immediate triage required to confirm scope and containment path.",
                "severity": severity,
                "status": status,
                "category": category,
                "source_ip": src,
                "target_asset": target,
                "mitre_tactic": tactic,
                "confidence_score": confidence,
                "detected_at": (base - timedelta(minutes=idx * 11)).isoformat(),
                "remediation_steps": [
                    "Contain the affected endpoint or identity.",
                    "Hunt for related indicators across SIEM and endpoint telemetry.",
                    "Execute remediation and verify no follow-on activity for one monitoring cycle.",
                ],
                "nist_function": nist,
                "tool_source": tool,
                "resolved_minutes": random.choice([14, 19, 25, 32]) if status in {"remediated", "closed"} else None,
                "lat": random.choice([50.1109, 53.3498, 52.3676, 48.8566, 40.4168, 52.2297]) + random.uniform(-0.25, 0.25),
                "lon": random.choice([8.6821, -6.2603, 4.9041, 2.3522, -3.7038, 21.0122]) + random.uniform(-0.25, 0.25),
            }
        )
    return out


def ensure_state() -> None:
    if "xp" not in st.session_state:
        st.session_state.xp = 240
    if "threats" not in st.session_state:
        st.session_state.threats = seed_threats()
    if "selected_threat_id" not in st.session_state and st.session_state.threats:
        st.session_state.selected_threat_id = st.session_state.threats[0]["id"]
    if "feed_filter" not in st.session_state:
        st.session_state.feed_filter = "all"
    if "kai_messages" not in st.session_state:
        st.session_state.kai_messages = [
            {
                "role": "assistant",
                "content": "Kai online. Select a threat and ask for tactical guidance; I will classify, map to NIST CSF, and provide next remediation steps.",
            }
        ]
    if "matrix_focus" not in st.session_state:
        st.session_state.matrix_focus = None
    if "auto_move_map" not in st.session_state:
        st.session_state.auto_move_map = False


def get_filtered_sorted_threats() -> list[dict]:
    all_threats = list(st.session_state.threats)
    if st.session_state.feed_filter == "all":
        subset = all_threats
    else:
        subset = [t for t in all_threats if t["severity"] == st.session_state.feed_filter]
    return sorted(subset, key=lambda t: t["detected_at"], reverse=True)


def get_selected_threat() -> dict | None:
    selected_id = st.session_state.get("selected_threat_id")
    for threat in st.session_state.threats:
        if threat["id"] == selected_id:
            return threat
    return st.session_state.threats[0] if st.session_state.threats else None


def calc_mttr_minutes(threats: list[dict]) -> int:
    resolved = [t["resolved_minutes"] for t in threats if t.get("resolved_minutes")]
    return int(sum(resolved) / len(resolved)) if resolved else 0


def get_defcon(threats: list[dict]) -> str:
    critical_open = sum(1 for t in threats if t["severity"] == "critical" and t["status"] not in {"remediated", "closed"})
    if critical_open >= 3:
        return "DEFCON 1"
    if critical_open == 2:
        return "DEFCON 2"
    if critical_open == 1:
        return "DEFCON 3"
    return "DEFCON 4"


def render_header(threats: list[dict]) -> None:
    defcon = get_defcon(threats)
    st.markdown(
        f"""
        <div class="sticky-header">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;">
                <div style="font-weight:800;font-size:18px;color:#22d3ee;">SECUREX COMMAND · Adaptive SOC AI Framework</div>
                <div>
                    <span class="chip" style="background:#1e293b;color:#f59e0b;border:1px solid #f59e0b;">{defcon}</span>
                    <span class="chip" style="margin-left:8px;background:#1e293b;color:#a78bfa;border:1px solid #a78bfa;">CYBER RANGE · LIVE FIRE</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats_bar(threats: list[dict]) -> None:
    df = pd.DataFrame(threats)
    total = len(df)
    critical = int((df["severity"] == "critical").sum()) if not df.empty else 0
    remediated = int(df["status"].isin(["remediated", "closed"]).sum()) if not df.empty else 0
    mttr = calc_mttr_minutes(threats)
    cards = [
        ("Active Threats", total),
        ("Critical", critical),
        ("Remediated", remediated),
        ("MTTR (min)", mttr),
    ]
    c1, c2, c3, c4 = st.columns(4)
    columns = [c1, c2, c3, c4]
    severity_mix = [
        ("critical", int((df["severity"] == "critical").sum()) if not df.empty else 0),
        ("high", int((df["severity"] == "high").sum()) if not df.empty else 0),
        ("medium", int((df["severity"] == "medium").sum()) if not df.empty else 0),
        ("low", int((df["severity"] == "low").sum()) if not df.empty else 0),
        ("info", int((df["severity"] == "info").sum()) if not df.empty else 0),
    ]
    stripes = "".join(
        f"<span style='display:block;height:6px;width:{(count / max(total,1))*100:.2f}%;background:{SEVERITY_COLOR[key]};float:left;'></span>"
        for key, count in severity_mix
    )
    for idx, (label, value) in enumerate(cards):
        with columns[idx]:
            st.metric(label, value)
            st.markdown(f"<div style='width:100%;overflow:hidden;border-radius:99px;border:1px solid rgba(148,163,184,.3)'>{stripes}</div>", unsafe_allow_html=True)


def render_feed(threats: list[dict]) -> None:
    st.subheader("Live Threat Feed")
    filter_choice = st.radio("Filter", ["all", "critical", "high", "medium", "low"], horizontal=True, index=["all", "critical", "high", "medium", "low"].index(st.session_state.feed_filter))
    st.session_state.feed_filter = filter_choice
    feed_threats = get_filtered_sorted_threats()
    for threat in feed_threats:
        color = SEVERITY_COLOR[threat["severity"]]
        selected = threat["id"] == st.session_state.selected_threat_id
        st.markdown(
            f"""
            <div class="feed-card" style="border-left-color:{color};{'box-shadow:0 0 0 1px #22d3ee inset;' if selected else ''}">
                <div style="display:flex;justify-content:space-between;gap:8px;">
                    <span class="chip" style="background:{color};color:#020617;">{threat['severity']}</span>
                    <span class="chip" style="background:#1e293b;color:#cbd5e1;border:1px solid #475569;">{threat['status']}</span>
                </div>
                <div style="margin-top:6px;font-weight:700;">{threat['title']}</div>
                <div style="font-size:12px;color:#94a3b8;">{threat['source_ip']} → {threat['target_asset']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(f"Open {threat['id']}", key=f"open_{threat['id']}", use_container_width=True):
            st.session_state.selected_threat_id = threat["id"]
            st.rerun()


def award_xp(points: int) -> None:
    st.session_state.xp += points


def render_detail_panel(threat: dict | None) -> None:
    st.subheader("Threat Detail Panel")
    if threat is None:
        st.info("Select a threat from the feed.")
        return
    st.markdown(f"### {threat['title']}")
    st.markdown(f"**Severity:** {threat['severity']}  \n**Category:** {threat['category']}  \n**Status:** {threat['status']}")
    st.write(threat["description"])

    m1, m2 = st.columns(2)
    with m1:
        st.write(f"**Source:** {threat['source_ip']}")
        st.write(f"**MITRE Tactic:** {threat['mitre_tactic']}")
        st.write(f"**NIST Function:** {threat['nist_function']}")
    with m2:
        st.write(f"**Target Asset:** {threat['target_asset']}")
        st.write(f"**Confidence:** {threat['confidence_score']}%")
        st.write(f"**Detection Tool:** {threat['tool_source']}")

    st.markdown("**Remediation Playbook**")
    for idx, step in enumerate(threat["remediation_steps"], start=1):
        st.write(f"{idx}. {step}")

    left, right = st.columns(2)
    with left:
        if st.button("Mark Remediated", use_container_width=True):
            if threat["status"] not in {"remediated", "closed"}:
                threat["status"] = "remediated"
                threat["resolved_minutes"] = random.choice([11, 17, 24])
                award_xp(120)
                st.success(f"{threat['id']} marked remediated. +120 XP")
                st.rerun()
            else:
                st.info("Threat already remediated/closed.")
    with right:
        if st.button("Ask Analyst Kai", use_container_width=True):
            st.session_state.kai_prefill = f"Guide triage for {threat['id']} ({threat['mitre_tactic']})"
            st.rerun()


def kai_response(query: str, threat: dict | None) -> str:
    if threat is None:
        return "No threat selected. Pick one from the feed and retry."
    return (
        "### 1) Threat Classification\n"
        f"- Type: {threat['category']}\n"
        f"- Likely MITRE ATT&CK tactic: {threat['mitre_tactic']}\n\n"
        "### 2) Why This Matters\n"
        f"- This activity targets **{threat['target_asset']}** and can escalate impact if not contained.\n\n"
        "### 3) NIST CSF Mapping\n"
        f"- Primary function: **{threat['nist_function'].title()}**\n\n"
        "### 4) Next Remediation Steps\n"
        "- Isolate affected identity/host and preserve forensic artifacts.\n"
        "- Correlate adjacent alerts to confirm blast radius.\n"
        "- Validate containment, then harden controls against recurrence."
    )


def render_kai_panel(threat: dict | None) -> None:
    st.subheader("AI Security Analyst Kai")
    st.caption("SLM MENTOR · ONLINE")
    for msg in st.session_state.kai_messages[-6:]:
        role = "You" if msg["role"] == "user" else "Kai"
        st.markdown(f"**{role}:** {msg['content']}")

    with st.form("kai_form", clear_on_submit=True):
        default = st.session_state.pop("kai_prefill", "")
        query = st.text_input("Ask Kai", value=default, placeholder="Ask about the selected threat, MITRE path, or NIST response.")
        submitted = st.form_submit_button("Send", use_container_width=True)
    if submitted and query.strip():
        st.session_state.kai_messages.append({"role": "user", "content": query.strip()})
        st.session_state.kai_messages.append({"role": "assistant", "content": kai_response(query.strip(), threat)})
        st.rerun()


def rank_from_xp(xp: int) -> tuple[str, int, int]:
    tiers = [
        ("Sentinel Initiate", 0),
        ("Threat Analyst", 300),
        ("SOC Operator", 800),
        ("Incident Commander", 1500),
        ("Digital Sovereign", 3000),
    ]
    current = tiers[0]
    nxt = (tiers[0][0], 300)
    for index, tier in enumerate(tiers):
        if xp >= tier[1]:
            current = tier
            if index + 1 < len(tiers):
                nxt = tiers[index + 1]
            else:
                nxt = (tier[0], tier[1])
    return current[0], current[1], nxt[1]


def render_ranking() -> None:
    st.subheader("Defense Ranking")
    rank, floor, next_xp = rank_from_xp(st.session_state.xp)
    st.write(f"**Current Rank:** {rank}")
    progress = 1.0 if next_xp == floor else (st.session_state.xp - floor) / (next_xp - floor)
    st.progress(max(0.0, min(1.0, progress)), text=f"XP {st.session_state.xp} / {next_xp}")


def severity_weight(severity: str) -> int:
    return dict(SEVERITY_WEIGHT_CHOICES).get(severity, 1)


def cell_color(score: int) -> str:
    if score <= 0:
        return "#1e293b"
    if score <= 4:
        return "#0ea5e9"
    if score <= 8:
        return "#f59e0b"
    if score <= 12:
        return "#f97316"
    return "#ef4444"


def _matrix_row_from_threat_id(threat_id: str) -> int:
    return sum(ord(ch) for ch in threat_id) % 3


def render_attack_matrix(threats: list[dict]) -> None:
    st.subheader("MITRE ATT&CK Matrix Heatmap")
    st.markdown(
        """
        <div class="legend">
            <span class="legend-pill" style="background:#1e293b;">Idle</span>
            <span class="legend-pill" style="background:#0ea5e9;">Low</span>
            <span class="legend-pill" style="background:#f59e0b;">Active</span>
            <span class="legend-pill" style="background:#f97316;">High</span>
            <span class="legend-pill" style="background:#ef4444;">Critical</span>
            <span class="legend-pill">🟢 Remediated present</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tactic_names = [name for _, name in TACTICS]
    tactic_labels = [f"{code} {name}" for code, name in TACTICS]
    y_layers = ["Layer 1", "Layer 2", "Layer 3"]

    open_counts = [[0 for _ in tactic_names] for _ in range(3)]
    resolved_counts = [[0 for _ in tactic_names] for _ in range(3)]
    for threat in threats:
        tactic = threat["mitre_tactic"]
        if tactic not in tactic_names:
            continue
        row = _matrix_row_from_threat_id(threat["id"])
        col = TACTIC_ORDER[tactic]
        if threat["status"] in {"remediated", "closed"}:
            resolved_counts[row][col] += 1
        else:
            open_counts[row][col] += severity_weight(threat["severity"])

    z = []
    text = []
    customdata = []
    for row_index in range(3):
        z_row = []
        text_row = []
        custom_row = []
        for col_index, tactic in enumerate(tactic_names):
            open_score = open_counts[row_index][col_index]
            resolved = resolved_counts[row_index][col_index]
            z_row.append(open_score)
            text_row.append(f"{open_score}\nR{resolved}")
            custom_row.append(
                [
                    tactic,
                    y_layers[row_index],
                    TACTIC_TO_TECHNIQUES[tactic][row_index],
                    open_score,
                    resolved,
                ]
            )
        z.append(z_row)
        text.append(text_row)
        customdata.append(custom_row)

    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=tactic_labels,
            y=y_layers,
            customdata=customdata,
            text=text,
            texttemplate="%{text}",
            colorscale=[
                [0.0, "#1e293b"],
                [0.25, "#0ea5e9"],
                [0.5, "#f59e0b"],
                [0.75, "#f97316"],
                [1.0, "#ef4444"],
            ],
            zmin=0,
            zmax=16,
            hovertemplate=(
                "Tactic: %{customdata[0]}<br>"
                "Layer: %{customdata[1]}<br>"
                "Technique: %{customdata[2]}<br>"
                "Signal Count: %{customdata[3]}<br>"
                "Resolved: %{customdata[4]}<extra></extra>"
            ),
            showscale=False,
        )
    )
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(tickangle=-28)

    selection = st.plotly_chart(
        fig,
        use_container_width=True,
        key="attack_matrix_heatmap",
        on_select="rerun",
        selection_mode=("points",),
    )
    selected_points = (selection or {}).get("selection", {}).get("points", [])
    if selected_points:
        point = selected_points[-1]
        custom = point.get("customdata")
        if custom and len(custom) >= 5:
            st.session_state.matrix_focus = {
                "tactic": custom[0],
                "layer": custom[1],
                "technique": custom[2],
                "signal_count": custom[3],
                "resolved": custom[4],
            }

    focus = st.session_state.get("matrix_focus")
    if focus:
        st.info(
            f"Focused cell: {focus['tactic']} / {focus['layer']} · "
            f"{focus['technique']} · signals={focus['signal_count']} · resolved={focus['resolved']}"
        )


def render_stack_topology() -> None:
    st.subheader("Security Stack Topology")
    cols = st.columns(4)
    for idx, (tool, role) in enumerate(STACK):
        with cols[idx % 4]:
            st.markdown(
                f"<div class='stack-card'><span class='status-dot'></span><strong>{tool}</strong><br><span style='font-size:12px;color:#94a3b8;'>{role}</span></div>",
                unsafe_allow_html=True,
            )


def render_geomap(threats: list[dict]) -> None:
    st.subheader("Threat Geomap")
    if not threats:
        st.info("No active telemetry.")
        return

    controls_left, controls_right = st.columns(2)
    with controls_left:
        if st.button("Advance Attack Movement", use_container_width=True):
            move_threat_positions()
            st.rerun()
    with controls_right:
        st.session_state.auto_move_map = st.toggle(
            "Auto-move on refresh",
            value=st.session_state.auto_move_map,
            key="auto_move_toggle",
        )

    if st.session_state.auto_move_map:
        move_threat_positions()

    df = pd.DataFrame(threats)
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        color="severity",
        hover_name="id",
        hover_data={"title": True, "status": True, "mitre_tactic": True, "lat": False, "lon": False},
        custom_data=["id", "title", "status", "mitre_tactic"],
        size=df["severity"].map(SEVERITY_SCORE),
        projection="natural earth",
    )
    fig.update_traces(marker=dict(opacity=0.88, line=dict(width=1, color="#0f172a")))
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
    selection = st.plotly_chart(
        fig,
        use_container_width=True,
        key="threat_geomap",
        on_select="rerun",
        selection_mode=("points", "box", "lasso"),
    )
    selected_points = (selection or {}).get("selection", {}).get("points", [])
    if selected_points:
        custom = selected_points[-1].get("customdata")
        if custom and len(custom) > 0:
            st.session_state.selected_threat_id = custom[0]
            st.success(f"Map focus set to {custom[0]}")


def move_threat_positions() -> None:
    for threat in st.session_state.threats:
        if threat["status"] in {"remediated", "closed"}:
            continue
        threat["lat"] += random.uniform(-0.12, 0.12)
        threat["lon"] += random.uniform(-0.12, 0.12)


def inject_simulated_attack() -> None:
    tactic = random.choice([name for _, name in TACTICS])
    sev = random.choices([k for k, _ in SEVERITY_WEIGHT_CHOICES], [w for _, w in SEVERITY_WEIGHT_CHOICES], k=1)[0]
    threat = {
        "id": f"THR-SIM-{random.randint(1000, 9999)}",
        "title": f"Simulated {sev.title()} event on {tactic}",
        "description": "Synthetic attack generated for cyber range training and live triage drills.",
        "severity": sev,
        "status": "new",
        "category": random.choice(["malware", "phishing", "lateral_movement", "zero_day"]),
        "source_ip": f"203.0.113.{random.randint(10, 220)}",
        "target_asset": random.choice(["api-gateway-01", "k8s-node-03", "idp-service-02", "db-primary-01"]),
        "mitre_tactic": tactic,
        "confidence_score": random.randint(62, 97),
        "detected_at": now_iso(),
        "remediation_steps": [
            "Validate event authenticity and preserve timeline evidence.",
            "Apply containment controls for impacted identity/asset.",
            "Run post-containment validation and update runbook knowledge.",
        ],
        "nist_function": random.choice(["identify", "protect", "detect", "respond", "recover"]),
        "tool_source": random.choice([tool for tool, _ in STACK]),
        "resolved_minutes": None,
        "lat": random.choice([50.1109, 53.3498, 52.3676, 48.8566, 40.4168, 52.2297]) + random.uniform(-0.2, 0.2),
        "lon": random.choice([8.6821, -6.2603, 4.9041, 2.3522, -3.7038, 21.0122]) + random.uniform(-0.2, 0.2),
    }
    st.session_state.threats.append(threat)
    st.session_state.selected_threat_id = threat["id"]


def render_sidebar() -> None:
    with st.sidebar:
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=170)
        st.caption("SecureX Command SOC Simulator")
        st.write("Portfolio demo mode: public interactive training.")
        if st.button("Inject Simulated Attack", use_container_width=True):
            inject_simulated_attack()
            st.rerun()


def render_dashboard() -> None:
    inject_css()
    threats = st.session_state.threats
    render_header(threats)
    render_sidebar()
    render_stats_bar(threats)
    tab_overview, tab_triage, tab_matrix, tab_stack = st.tabs(
        ["Command Overview", "Triage Console", "MITRE Matrix", "Security Stack"]
    )

    with tab_overview:
        left, right = st.columns([1.1, 1.4])
        with left:
            render_feed(threats)
        with right:
            render_geomap(threats)

    with tab_triage:
        selected = get_selected_threat()
        left, right = st.columns([1.2, 1.0])
        with left:
            render_detail_panel(selected)
        with right:
            render_kai_panel(selected)
            st.divider()
            render_ranking()

    with tab_matrix:
        render_attack_matrix(threats)

    with tab_stack:
        render_stack_topology()


def main() -> None:
    ensure_state()
    render_dashboard()


if __name__ == "__main__":
    main()
