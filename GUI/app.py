import json
import os
import random
import base64
from datetime import datetime, timedelta, timezone
from urllib import error as url_error
from urllib import request as url_request

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from google import genai
from google.genai import errors as genai_errors


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

KAI_SYSTEM_PROMPT = """SYSTEM PROMPT: Operational Readiness as Code.

You are AI Security Analyst Kai, embedded in SECUREX COMMAND. This platform builds the next generation Infrastructure as Code cyber range and SOC readiness experience.

Mission:
- Prepare cybersecurity professionals like flight simulators prepare pilots.
- Treat scenarios as code, think modular design, and keep training gamified and mission-focused.
- Guide analysts through investigations with coaching that measures operational readiness, not pass/fail outcomes.
- Prefer refactoring and incremental improvement over rewriting from scratch.
- Keep engineering quality high and user experience clean so the product feels like a new cybersecurity category, not just another dashboard.

Your role is to guide users through identifying, classifying, and triaging every Threat in the system.

For any user question or selected threat, you must:
1. CLASSIFY: Identify the threat type and map it to the MITRE ATT&CK tactic (e.g. TA0001 Initial Access, TA0006 Credential Access, TA0004 Privilege Escalation, TA0008 Lateral Movement, TA0009 Collection, TA0010 Exfiltration, TA0011 Command & Control, TA0040 Impact).
2. EXPLAIN THE WHY: In plain language a student can learn from, explain why this threat matters, what an attacker is attempting, and what business impact it carries.
3. MAP TO NIST: Map the recommended response to the NIST Cybersecurity Framework functions — Identify, Protect, Detect, Respond, Recover.
4. REMEDIATE: Give 2-3 concrete, ordered next remediation steps the analyst should take.
5. ENCOURAGE: Close with a brief note on what the analyst just learned or a tip to improve detection going forward.

You have read access to the Threat entity. When a user asks about the threat landscape, list and summarize the active threats, calling out severity, category, source, target asset, MITRE tactic, confidence, and NIST function. Prioritize critical and high-severity signals.

Tone: calm, tactical, precise, encouraging. Speak like an experienced SOC lead walking a junior analyst through their shift. Use short headers and structure. Never fabricate data that is not in the Threat entity or the user's message — if you do not know, say so and recommend enrichment."""


def _safe_secret(name: str):
    try:
        return st.secrets.get(name)
    except FileNotFoundError:
        return None


def _get_gemini_settings() -> tuple[str | None, str]:
    api_key = _safe_secret("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model = _safe_secret("GEMINI_MODEL") or os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
    return api_key, model


def _gemini_candidate_models(preferred: str) -> list[str]:
    candidates = [
        preferred,
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ]
    deduped = []
    seen = set()
    for model in candidates:
        if model and model not in seen:
            deduped.append(model)
            seen.add(model)
    return deduped


def _get_nextjs_app_url() -> str | None:
    return (
        _safe_secret("NEXTJS_APP_URL")
        or os.getenv("NEXTJS_APP_URL")
        or os.getenv("NEXT_APP_URL")
        or os.getenv("WEB_APP_URL")
    )


def _probe_nextjs_url(url: str) -> tuple[bool, str]:
    try:
        req = url_request.Request(url, headers={"User-Agent": "securex-streamlit-bridge"})
        with url_request.urlopen(req, timeout=8) as response:
            status = getattr(response, "status", 200)
            if 200 <= status < 400:
                return True, f"Connected (HTTP {status})"
            return False, f"Endpoint returned HTTP {status}"
    except url_error.HTTPError as exc:
        return False, f"HTTP {exc.code}: {exc.reason}"
    except url_error.URLError as exc:
        return False, f"URL error: {exc.reason}"
    except TimeoutError:
        return False, "Connection timed out"


def render_nextjs_bridge() -> bool:
    nextjs_url = _get_nextjs_app_url()
    if not nextjs_url:
        return False
    if "your-vercel-url" in nextjs_url:
        st.error("NEXTJS_APP_URL is still a placeholder. Set it to your real deployed Next.js URL.")
        st.caption("Example: https://adaptive-soc-ai-framework.vercel.app")
        return False
    if not nextjs_url.startswith(("http://", "https://")):
        st.error("NEXTJS_APP_URL must start with http:// or https://")
        return False
    reachable, probe_message = _probe_nextjs_url(nextjs_url)

    st.markdown("## SECUREX COMMAND · Enterprise UI")
    st.caption("Streamlit bridge mode is active.")
    if reachable:
        st.success(f"Next.js endpoint check: {probe_message}")
    else:
        st.error(f"Next.js endpoint check failed: {probe_message}")

    st.link_button("Open enterprise UI in new tab", nextjs_url, use_container_width=True)
    st.caption("If your host blocks iframe embedding, use the button above (recommended).")

    if reachable and st.toggle("Embed enterprise UI inside Streamlit", value=False, key="embed_nextjs_iframe"):
        components.iframe(nextjs_url, height=980, scrolling=True)
    return True


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
        .alert-beacon-wrap {
          display:inline-flex; align-items:center; gap:6px; margin-right:10px;
          padding:2px 8px; border-radius:999px;
          border:1px solid rgba(239,68,68,.55); background: rgba(127, 29, 29, .3);
        }
        .alert-beacon-dot {
          width:10px; height:10px; border-radius:999px; background:#ef4444;
          box-shadow:0 0 0 rgba(239,68,68,.7); animation: beaconPulse 1.15s infinite;
        }
        .alert-beacon-text {
          color:#fca5a5; font-size:11px; font-weight:800; letter-spacing:.03em; text-transform:uppercase;
        }
        .range-beacon-wrap {
          display:inline-flex; align-items:center; gap:6px; margin-left:8px;
          padding:2px 8px; border-radius:999px;
          border:1px solid rgba(34,197,94,.55); background: rgba(20, 83, 45, .3);
        }
        .range-beacon-dot {
          width:10px; height:10px; border-radius:999px; background:#22c55e;
          box-shadow:0 0 0 rgba(34,197,94,.7); animation: rangePulse 1.15s infinite;
        }
        .range-beacon-text {
          color:#86efac; font-size:11px; font-weight:800; letter-spacing:.03em; text-transform:uppercase;
        }
        @keyframes beaconPulse {
          0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239,68,68,.8); opacity: 1; }
          70% { transform: scale(1.1); box-shadow: 0 0 0 12px rgba(239,68,68,0); opacity: .9; }
          100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239,68,68,0); opacity: 1; }
        }
        @keyframes rangePulse {
          0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(34,197,94,.8); opacity: 1; }
          70% { transform: scale(1.1); box-shadow: 0 0 0 12px rgba(34,197,94,0); opacity: .9; }
          100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(34,197,94,0); opacity: 1; }
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


def now_epoch() -> float:
    return datetime.now(timezone.utc).timestamp()


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
        st.session_state.threats = []
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
    if "active_dashboard_tab" not in st.session_state:
        st.session_state.active_dashboard_tab = "Command Overview"
    if "escalation_log" not in st.session_state:
        st.session_state.escalation_log = []
    if "public_chat_messages" not in st.session_state:
        st.session_state.public_chat_messages = [
            {
                "role": "assistant",
                "content": "Welcome to the AI Security Analyst Kai chat. Ask about SOC triage, MITRE ATT&CK, NIST response mapping, or this simulator.",
            }
        ]
    if "public_chat_provider_status" not in st.session_state:
        api_key, model = _get_gemini_settings()
        st.session_state.public_chat_provider_status = (
            f"Gemini configured ({model})" if api_key else "Local fallback (no API key configured)"
        )
    if "auto_attack_enabled" not in st.session_state:
        st.session_state.auto_attack_enabled = False
    if "auto_attack_interval_min" not in st.session_state:
        st.session_state.auto_attack_interval_min = 1
    if "auto_attack_include_ai" not in st.session_state:
        st.session_state.auto_attack_include_ai = True
    if "last_auto_attack_epoch" not in st.session_state:
        st.session_state.last_auto_attack_epoch = now_epoch()
    if "auto_attack_first_wave_pending" not in st.session_state:
        st.session_state.auto_attack_first_wave_pending = False
    if "auto_attack_first_wave_epoch" not in st.session_state:
        st.session_state.auto_attack_first_wave_epoch = now_epoch()
    if "last_auto_move_epoch" not in st.session_state:
        st.session_state.last_auto_move_epoch = now_epoch()
    if "last_map_move_message" not in st.session_state:
        st.session_state.last_map_move_message = ""
    if "report_submission_log" not in st.session_state:
        st.session_state.report_submission_log = []
    if "auto_incoming_attacks_toggle" not in st.session_state:
        st.session_state.auto_incoming_attacks_toggle = st.session_state.auto_attack_enabled
    if "auto_attack_interval_selector" not in st.session_state:
        st.session_state.auto_attack_interval_selector = st.session_state.auto_attack_interval_min
    if "include_ai_driven_attacks_toggle" not in st.session_state:
        st.session_state.include_ai_driven_attacks_toggle = st.session_state.auto_attack_include_ai


def _playbook_catalog(threat: dict) -> list[dict]:
    tactic = threat.get("mitre_tactic", "")
    ai_related = _is_ai_related_threat(threat)
    playbooks = [
        {
            "name": "Identity Lockdown Sprint",
            "fit_tactics": {"Credential Access", "Initial Access", "Privilege Escalation"},
            "score": 76,
            "steps": [
                "Force password + token reset and revoke active sessions.",
                "Block source IP ranges and harden MFA challenges.",
                "Revalidate SSO and IAM audit trails.",
            ],
        },
        {
            "name": "Containment and Host Isolation",
            "fit_tactics": {"Lateral Movement", "Command & Control", "Impact"},
            "score": 80,
            "steps": [
                "Isolate impacted endpoint/segment from trust paths.",
                "Deploy IOC blocks across EDR, firewall, and proxy.",
                "Run rapid sweep for sibling compromise indicators.",
            ],
        },
        {
            "name": "Data Exfiltration Shutdown",
            "fit_tactics": {"Collection", "Exfiltration"},
            "score": 78,
            "steps": [
                "Freeze egress channel and rotate exposed credentials.",
                "Preserve transfer logs and cloud object access traces.",
                "Apply DLP and monitor for repeated extraction attempts.",
            ],
        },
        {
            "name": "Threat Hunt and Intelligence Correlation",
            "fit_tactics": {"Initial Access", "Lateral Movement", "Command & Control"},
            "score": 74,
            "steps": [
                "Pivot across SIEM telemetry for timeline confirmation.",
                "Correlate with external CTI and ATT&CK techniques.",
                "Promote validated indicators to shared detection content.",
            ],
        },
        {
            "name": "AI Guardrail and Model Abuse Response",
            "fit_tactics": {"Collection", "Command & Control", "Impact"},
            "score": 72,
            "steps": [
                "Quarantine suspicious prompt channels and model endpoints.",
                "Activate prompt filtering, rate limits, and output controls.",
                "Review model logs for poisoning or data-leak indicators.",
            ],
        },
    ]
    for item in playbooks:
        if tactic in item["fit_tactics"]:
            item["score"] += 14
        if ai_related and "AI Guardrail" in item["name"]:
            item["score"] += 18
        if ai_related and "Threat Hunt" in item["name"]:
            item["score"] += 8
        item["score"] = max(1, min(100, item["score"]))
    playbooks.sort(key=lambda x: x["score"], reverse=True)
    return playbooks


def render_playbook_recommendations(threat: dict, key_suffix: str) -> dict:
    st.markdown("#### Recommended Playbooks")
    st.info("Recommendation before selection: review threat TTPs and CTI sources first.")
    l1, l2, l3 = st.columns(3)
    with l1:
        st.link_button("Review MITRE ATT&CK", "https://attack.mitre.org/", use_container_width=True)
    with l2:
        st.link_button("Review ATT&CK Navigator", "https://mitre-attack.github.io/attack-navigator/", use_container_width=True)
    with l3:
        st.link_button("Review OpenCTI", "https://www.opencti.io/", use_container_width=True)

    options = _playbook_catalog(threat)
    labels = [f"{entry['name']} ({entry['score']}%)" for entry in options]
    selected_label = st.radio(
        "Choose playbook",
        labels,
        index=0,
        key=_workflow_key(threat["id"], f"playbook_choice_{key_suffix}"),
    )
    selected_entry = options[labels.index(selected_label)]
    st.success(f"Best option right now: {options[0]['name']} ({options[0]['score']}% estimated success)")

    st.markdown(f"**Selected playbook:** {selected_entry['name']} · **Estimated success:** {selected_entry['score']}%")
    for idx, step in enumerate(selected_entry["steps"], start=1):
        st.write(f"{idx}. {step}")
    st.session_state[_workflow_key(threat["id"], "selected_playbook_name")] = selected_entry["name"]
    st.session_state[_workflow_key(threat["id"], "selected_playbook_score")] = selected_entry["score"]
    return selected_entry


def render_case_workspace(threat: dict | None) -> None:
    st.subheader("Case Workspace")
    if threat is None:
        st.info("Select a case from the feed or geomap to open the dedicated case workspace.")
        return
    st.markdown(
        f"### {threat['id']} · {threat['title']}\n"
        f"**Severity:** {threat['severity']} · **Status:** {threat['status']} · "
        f"**MITRE:** {threat['mitre_tactic']} · **NIST:** {threat['nist_function'].title()}"
    )
    st.write(threat["description"])
    render_playbook_recommendations(threat, "case_workspace")
    if st.button("Open Incident Workflow for this case", use_container_width=True, key=_workflow_key(threat["id"], "open_workflow")):
        st.session_state.active_dashboard_tab = "Incident Workflow"
        st.rerun()


def get_filtered_sorted_threats() -> list[dict]:
    all_threats = list(st.session_state.threats)
    if st.session_state.feed_filter == "all":
        subset = all_threats
    else:
        subset = [t for t in all_threats if t["severity"] == st.session_state.feed_filter]
    return sorted(subset, key=lambda t: t["detected_at"], reverse=False)


def summarize_active_threats() -> str:
    active = [t for t in st.session_state.threats if t["status"] not in {"remediated", "closed"}]
    ordered = sorted(
        active,
        key=lambda t: (0 if t["severity"] == "critical" else 1 if t["severity"] == "high" else 2, t["detected_at"]),
    )
    if not ordered:
        return "No active threats currently in the Threat entity."
    lines = []
    for threat in ordered[:8]:
        lines.append(
            f"- {threat['id']} | sev={threat['severity']} | category={threat['category']} | "
            f"source={threat['source_ip']} | target={threat['target_asset']} | "
            f"mitre={threat['mitre_tactic']} | confidence={threat['confidence_score']} | "
            f"nist={threat['nist_function']}"
        )
    return "\n".join(lines)


def get_selected_threat() -> dict | None:
    selected_id = st.session_state.get("selected_threat_id")
    for threat in st.session_state.threats:
        if threat["id"] == selected_id:
            return threat
    return st.session_state.threats[0] if st.session_state.threats else None


def calc_mttr_minutes(threats: list[dict]) -> int:
    resolved = [t["resolved_minutes"] for t in threats if t.get("resolved_minutes")]
    return int(sum(resolved) / len(resolved)) if resolved else 0


def get_soc_emergency_index(threats: list[dict]) -> int:
    incoming_alerts = sum(1 for threat in threats if threat["status"] not in {"remediated", "closed"})
    return incoming_alerts // 3


def render_header(threats: list[dict]) -> None:
    emergency_index = get_soc_emergency_index(threats)
    incoming_count = sum(1 for t in threats if t["status"] not in {"remediated", "closed"})
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")
    logo_html = '<div style="font-weight:800;font-size:18px;color:#22d3ee;">SECUREX COMMAND</div>'
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as logo_file:
            logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
        logo_html = (
            f'<img src="data:image/png;base64,{logo_b64}" alt="SECUREX logo" '
            'style="height:330px;width:auto;display:block;" />'
        )
    st.markdown(
        f"""
        <div class="sticky-header">
            <div style="position:relative;display:flex;justify-content:flex-end;align-items:center;min-height:304px;">
                <div style="position:absolute;left:50%;top:50%;transform:translate(-50%, -50%);display:flex;justify-content:center;align-items:center;">
                    {logo_html}
                </div>
                <div style="display:flex;justify-content:flex-end;align-items:center;position:relative;z-index:2;">
                    <span class="alert-beacon-wrap">
                        <span class="alert-beacon-dot"></span>
                        <span class="alert-beacon-text">Incoming alerts: {incoming_count}</span>
                    </span>
                    <span class="chip" style="background:#1e293b;color:#f59e0b;border:1px solid #f59e0b;">SOC Emergency Index: {emergency_index}</span>
                    <span class="range-beacon-wrap">
                        <span class="range-beacon-dot"></span>
                        <span class="range-beacon-text">Cyber Range · Live</span>
                    </span>
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
    st.caption("Chronological order: oldest incidents to newest incidents.")
    filter_choice = st.radio("Filter", ["all", "critical", "high", "medium", "low"], horizontal=True, index=["all", "critical", "high", "medium", "low"].index(st.session_state.feed_filter))
    st.session_state.feed_filter = filter_choice
    feed_threats = get_filtered_sorted_threats()
    if not feed_threats:
        st.info("No threats match the current filter.")
        return

    table_df = pd.DataFrame(
        [
            {
                "ID": threat["id"],
                "Detected At": threat["detected_at"].replace("T", " ").replace("+00:00", " UTC"),
                "Severity": threat["severity"],
                "Status": threat["status"],
                "Title": threat["title"],
                "Source IP": threat["source_ip"],
                "Target": threat["target_asset"],
            }
            for threat in feed_threats
        ]
    )
    selection = st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="live_threat_feed_table",
    )
    selected_rows = (selection or {}).get("selection", {}).get("rows", [])
    if selected_rows:
        selected_row = selected_rows[0]
        selected_id = table_df.iloc[selected_row]["ID"]
        st.session_state.selected_threat_id = selected_id
        st.session_state.active_dashboard_tab = "Incident Workflow"
        st.rerun()

    selected = next((t for t in feed_threats if t["id"] == st.session_state.selected_threat_id), None)
    if selected:
        st.caption(f"Selected case: {selected['id']} · click any row to open Incident Workflow.")

    st.markdown("#### Quick open")
    st.caption("Use Open to jump directly into the Incident Workflow for a case.")
    for threat in feed_threats:
        open_col, detail_col = st.columns([0.22, 0.78])
        with open_col:
            if st.button(
                f"Open {threat['id']}",
                key=f"open_feed_case_{threat['id']}",
                use_container_width=True,
            ):
                st.session_state.selected_threat_id = threat["id"]
                st.session_state.active_dashboard_tab = "Incident Workflow"
                st.rerun()
        with detail_col:
            st.markdown(
                f"**{threat['title']}**  \n"
                f"Severity: `{threat['severity']}` · Status: `{threat['status']}` · "
                f"Target: `{threat['target_asset']}`"
            )


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
        if st.button("Ask AI Security Analyst Kai", use_container_width=True):
            st.session_state.kai_prefill = f"Guide triage for {threat['id']} ({threat['mitre_tactic']})"
            st.rerun()


def kai_response(query: str, threat: dict | None) -> str:
    if threat is None:
        return (
            "### Threat Classification\n"
            "- No threat is currently selected.\n\n"
            "### Why This Matters\n"
            "- Triage quality depends on specific threat telemetry context.\n\n"
            "### NIST Mapping\n"
            "- Start in Identify/Detect by selecting a threat and validating signal confidence.\n\n"
            "### Next Remediation Steps\n"
            "1. Select a threat from the feed.\n"
            "2. Review source/target/tactic details.\n"
            "3. Execute the workflow checklist.\n\n"
            "### Analyst Growth Tip\n"
            "- Great analysts always tie response actions to concrete evidence."
        )
    if "threat landscape" in query.lower() or "active threats" in query.lower():
        return (
            "### Active Threat Landscape\n"
            f"{summarize_active_threats()}\n\n"
            "### Analyst Growth Tip\n"
            "- Prioritize critical and high-severity cases first, then confirm containment evidence."
        )
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


def _fallback_public_chat_response(prompt: str, threat: dict | None) -> str:
    prompt_l = prompt.lower().strip()
    if prompt_l in {"live", "live?", "are you working", "are you working now", "are you working now?"}:
        return (
            "Yes — Kai is online in fallback mode right now.\n\n"
            "I can still guide triage with MITRE + NIST mapping while Gemini is unavailable."
        )

    if "threat landscape" in prompt.lower() or "active threats" in prompt.lower():
        return (
            "### Active Threat Landscape\n"
            f"{summarize_active_threats()}\n\n"
            "### Analyst Growth Tip\n"
            "- Build a repeatable triage sequence: classify, contain, validate, and document."
        )
    return kai_response(prompt, threat)


def _gemini_public_chat_response(prompt: str, threat: dict | None) -> str:
    api_key, model = _get_gemini_settings()
    if not api_key:
        st.session_state.public_chat_provider_status = "Local fallback (no API key configured)"
        return _fallback_public_chat_response(prompt, threat)

    context = "No specific incident selected."
    if threat:
        context = (
            f"Case={threat['id']}, Severity={threat['severity']}, "
            f"Tactic={threat['mitre_tactic']}, Target={threat['target_asset']}, Status={threat['status']}"
        )
    threat_landscape = summarize_active_threats()
    full_prompt = (
        f"{KAI_SYSTEM_PROMPT}\n\n"
        f"Threat entity (active summary):\n{threat_landscape}\n\n"
        f"Selected threat context: {context}\n"
        f"User question: {prompt}\n"
    )
    client = genai.Client(api_key=api_key)
    last_error = None
    for candidate_model in _gemini_candidate_models(model):
        try:
            response = client.models.generate_content(model=candidate_model, contents=full_prompt)
            if response and getattr(response, "text", None):
                st.session_state.public_chat_provider_status = f"Gemini live ({candidate_model})"
                return response.text
            last_error = f"Empty response from model {candidate_model}"
        except (
            genai_errors.APIError,
            genai_errors.ClientError,
            genai_errors.ServerError,
            genai_errors.UnknownApiResponseError,
        ) as exc:
            last_error = str(exc)
            error_text = str(exc).lower()
            if "not found" in error_text or "is not supported" in error_text or "404" in error_text:
                continue
            st.session_state.public_chat_provider_status = "Local fallback (Gemini unavailable)"
            return _fallback_public_chat_response(prompt, threat)

    fallback_response = _fallback_public_chat_response(prompt, threat)
    st.session_state.public_chat_provider_status = "Local fallback (Gemini model unavailable)"
    if last_error:
        return (
            f"{fallback_response}\n\n"
            f"_Gemini fallback notice: primary model unavailable ({last_error})._"
        )
    return fallback_response


def render_public_chat(threat: dict | None) -> None:
    st.subheader("Public AI Chat")
    api_key, model = _get_gemini_settings()
    status = st.session_state.get("public_chat_provider_status", "Unknown")
    st.caption(f"Provider: {status} · Configured model: {model if api_key else 'Rule-based'}")

    for msg in st.session_state.public_chat_messages[-8:]:
        speaker = "You" if msg["role"] == "user" else "Kai"
        st.markdown(f"**{speaker}:** {msg['content']}")

    with st.form("public_chat_form", clear_on_submit=True):
        question = st.text_input("Ask a question", placeholder="How should I triage credential stuffing attacks?")
        sent = st.form_submit_button("Send", use_container_width=True)

    if sent and question.strip():
        st.session_state.public_chat_messages.append({"role": "user", "content": question.strip()})
        reply = _gemini_public_chat_response(question.strip(), threat)
        st.session_state.public_chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()


def _workflow_key(threat_id: str, suffix: str) -> str:
    return f"wf_{suffix}_{threat_id}"


def _tactic_code(tactic_name: str) -> str:
    for code, name in TACTICS:
        if name == tactic_name:
            return code
    return ""


def _is_ai_related_threat(threat: dict) -> bool:
    title = threat.get("title", "").lower()
    category = threat.get("category", "")
    return "ai" in title or "isolation forest" in title or category == "zero_day" or category.startswith("ai_")


def render_incident_workflow(threat: dict | None) -> None:
    st.subheader("Incident Workflow")
    if threat is None:
        st.info("Select a case from the Live Threat Feed to open workflow.")
        return

    st.markdown(
        f"### {threat['id']} · {threat['title']}\n"
        f"**Severity:** {threat['severity']} · **Status:** {threat['status']} · "
        f"**MITRE:** {threat['mitre_tactic']} · **NIST:** {threat['nist_function'].title()}"
    )
    st.write(threat["description"])

    st.markdown("#### Framework Navigator")
    tactic_code = _tactic_code(threat["mitre_tactic"])
    mitre_url = f"https://attack.mitre.org/tactics/{tactic_code}/" if tactic_code else "https://attack.mitre.org/tactics/"
    nist_url = "https://www.nist.gov/cyberframework"
    owasp_ai_url = "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
    owasp_general_url = "https://owasp.org/www-project-top-ten/"
    fw1, fw2, fw3 = st.columns(3)
    with fw1:
        st.link_button("Open MITRE ATT&CK", mitre_url, use_container_width=True)
    with fw2:
        st.link_button("Open NIST CSF", nist_url, use_container_width=True)
    with fw3:
        if _is_ai_related_threat(threat):
            st.link_button("Open OWASP for AI", owasp_ai_url, use_container_width=True)
        else:
            st.link_button("Open OWASP Top 10", owasp_general_url, use_container_width=True)

    selected_playbook = render_playbook_recommendations(threat, "workflow")
    playbook_col, escalation_col = st.columns([1.2, 1.0])
    with playbook_col:
        st.markdown("#### Isolation & Remediation Playbook")
        isolation_steps = [
            "Isolate affected host/identity from production trust paths.",
            "Block known indicators (IP/hash/domain) at perimeter and endpoint layers.",
            "Preserve volatile and disk forensics snapshots.",
        ]
        for idx, step in enumerate(isolation_steps, start=1):
            st.checkbox(step, key=_workflow_key(threat["id"], f"isolation_{idx}"))
        for idx, step in enumerate(threat["remediation_steps"], start=1):
            st.checkbox(step, key=_workflow_key(threat["id"], f"remediation_{idx}"))

        if st.button("Complete workflow and mark remediated", use_container_width=True, key=_workflow_key(threat["id"], "complete")):
            if threat["status"] not in {"remediated", "closed"}:
                threat["status"] = "remediated"
                threat["resolved_minutes"] = random.choice([11, 17, 24, 31])
                award_xp(150)
                st.success(f"{threat['id']} marked remediated. +150 XP")
                st.rerun()
            else:
                st.info("Case already remediated/closed.")

    with escalation_col:
        st.markdown("#### Escalation")
        escalate_to = st.selectbox(
            "Escalate to",
            ["SOC Tier 2", "SOC Tier 3", "Incident Command", "Threat Hunting Team", "Legal & Compliance"],
            key=_workflow_key(threat["id"], "escalate_to"),
        )
        priority = st.selectbox("Priority", ["P1", "P2", "P3"], key=_workflow_key(threat["id"], "priority"))
        reason = st.text_area("Escalation reason", key=_workflow_key(threat["id"], "reason"), height=100)
        if st.button("Escalate case", use_container_width=True, key=_workflow_key(threat["id"], "escalate")):
            log = {
                "time": now_iso(),
                "threat_id": threat["id"],
                "to": escalate_to,
                "priority": priority,
                "reason": reason.strip() or "No reason supplied.",
            }
            st.session_state.escalation_log.insert(0, log)
            threat["status"] = "investigating"
            st.success(f"Escalated successfully to {escalate_to} ({priority}) for case {threat['id']}.")
            st.rerun()

    st.markdown("#### Incident Report")
    report_template = (
        f"Case: {threat['id']}\n"
        f"Title: {threat['title']}\n"
        f"Severity: {threat['severity']}\n"
        f"Status: {threat['status']}\n"
        f"MITRE: {threat['mitre_tactic']}\n"
        "Findings:\n- \nActions taken:\n- \nRecommended next actions:\n- "
    )
    report_text = st.text_area(
        "Report draft",
        value=st.session_state.get(_workflow_key(threat["id"], "report"), report_template),
        key=_workflow_key(threat["id"], "report"),
        height=180,
    )
    report_payload = {
        "generated_at": now_iso(),
        "threat": threat,
        "selected_playbook": {"name": selected_playbook["name"], "score": selected_playbook["score"]},
        "report": report_text,
        "escalations": [x for x in st.session_state.escalation_log if x["threat_id"] == threat["id"]],
    }
    st.download_button(
        "Download incident report (JSON)",
        data=json.dumps(report_payload, indent=2),
        file_name=f"{threat['id']}-incident-report.json",
        mime="application/json",
        use_container_width=True,
        key=_workflow_key(threat["id"], "download_report"),
    )
    if st.button("Submit report to SOC escalation queue", use_container_width=True, key=_workflow_key(threat["id"], "submit_report")):
        target = st.session_state.get(_workflow_key(threat["id"], "escalate_to"), "SOC Tier 2")
        st.session_state.report_submission_log.insert(
            0,
            {
                "time": now_iso(),
                "threat_id": threat["id"],
                "target": target,
                "playbook": selected_playbook["name"],
                "success_estimate": selected_playbook["score"],
            },
        )
        st.success(
            f"Escalated successfully to {target}. "
            f"Report submitted with playbook '{selected_playbook['name']}' ({selected_playbook['score']}% fit)."
        )


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


def _matching_cases_for_focus(threats: list[dict], focus: dict) -> list[dict]:
    matches = [t for t in threats if t.get("mitre_tactic") == focus.get("tactic")]
    active = [t for t in matches if t.get("status") not in {"remediated", "closed"}]
    pool = active if active else matches
    return sorted(
        pool,
        key=lambda t: (
            -SEVERITY_SCORE.get(t.get("severity", "info"), 1),
            -int(t.get("confidence_score", 0)),
            t.get("detected_at", ""),
        ),
    )


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
        matches = _matching_cases_for_focus(threats, focus)
        tactic_code = _tactic_code(focus["tactic"])
        mitre_tactic_url = f"https://attack.mitre.org/tactics/{tactic_code}/" if tactic_code else "https://attack.mitre.org/tactics/"
        st.info(
            f"Focused cell: {focus['tactic']} / {focus['layer']} · "
            f"{focus['technique']} · signals={focus['signal_count']} · resolved={focus['resolved']}"
        )
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("Open MITRE ATT&CK tactic", mitre_tactic_url, use_container_width=True)
        with c2:
            if matches:
                best = matches[0]
                if st.button(
                    f"Open best case {best['id']}",
                    key=f"matrix_inline_best_{best['id']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_threat_id = best["id"]
                    st.session_state.active_dashboard_tab = "Incident Workflow"
                    st.rerun()
            else:
                st.button("Open best case (no match yet)", disabled=True, use_container_width=True)
        focus_key = f"{focus['tactic']}_{focus['layer']}".replace(" ", "_").replace("&", "and")
        with st.popover("Explain selected matrix cell and open a case", use_container_width=True):
            st.markdown("#### Cell explanation")
            st.write(
                f"This cell tracks **{focus['tactic']}** activity in **{focus['layer']}**. "
                f"Technique focus is **{focus['technique']}** with signal score **{focus['signal_count']}** "
                f"and **{focus['resolved']}** resolved events."
            )
            st.write(
                "Recommended triage flow: validate signal quality, isolate impacted identity/asset, "
                "and confirm containment evidence before closing."
            )
            if not matches:
                st.warning("No linked case is available for this tactic yet.")
            else:
                best = matches[0]
                st.success(
                    f"Best case to open now: {best['id']} ({best['severity']}, confidence {best['confidence_score']}%)."
                )
                if st.button(
                    f"Open best case {best['id']}",
                    key=f"matrix_open_best_{focus_key}",
                    use_container_width=True,
                ):
                    st.session_state.selected_threat_id = best["id"]
                    st.session_state.active_dashboard_tab = "Incident Workflow"
                    st.rerun()
                st.caption("Or open another matching case:")
                for case in matches[:5]:
                    if st.button(
                        f"Open {case['id']} · {case['title']}",
                        key=f"matrix_open_case_{focus_key}_{case['id']}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_threat_id = case["id"]
                        st.session_state.active_dashboard_tab = "Incident Workflow"
                        st.rerun()


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
            moved = move_threat_positions()
            st.session_state.last_map_move_message = f"Moved {moved} active threats on the geomap."
            st.rerun()
    with controls_right:
        st.session_state.auto_move_map = st.toggle(
            "Auto-move on refresh",
            value=st.session_state.auto_move_map,
            key="auto_move_toggle",
        )

    if st.session_state.auto_move_map:
        moved = move_threat_positions()
        st.session_state.last_map_move_message = f"Auto-move shifted {moved} active threats."
    if st.session_state.last_map_move_message:
        st.caption(st.session_state.last_map_move_message)

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
            st.session_state.active_dashboard_tab = "Case Workspace"
            st.rerun()

    st.markdown("#### Geomap quick open")
    st.caption("Open a mapped threat directly in Case Workspace.")
    for threat in threats:
        open_col, detail_col = st.columns([0.22, 0.78])
        with open_col:
            if st.button(
                f"Open {threat['id']}",
                key=f"open_map_case_{threat['id']}",
                use_container_width=True,
            ):
                st.session_state.selected_threat_id = threat["id"]
                st.session_state.active_dashboard_tab = "Case Workspace"
                st.rerun()
        with detail_col:
            st.markdown(
                f"**{threat['title']}**  \n"
                f"Severity: `{threat['severity']}` · Status: `{threat['status']}` · "
                f"Target: `{threat['target_asset']}`"
            )


def move_threat_positions() -> int:
    moved_count = 0
    for threat in st.session_state.threats:
        if threat["status"] in {"remediated", "closed"}:
            continue
        threat["lat"] = max(-85.0, min(85.0, threat["lat"] + random.uniform(-0.45, 0.45)))
        threat["lon"] = max(-180.0, min(180.0, threat["lon"] + random.uniform(-0.45, 0.45)))
        moved_count += 1
    return moved_count


def inject_simulated_attack(include_ai_driven: bool | None = None) -> None:
    include_ai = st.session_state.auto_attack_include_ai if include_ai_driven is None else include_ai_driven
    tactic = random.choice([name for _, name in TACTICS])
    sev = random.choices([k for k, _ in SEVERITY_WEIGHT_CHOICES], [w for _, w in SEVERITY_WEIGHT_CHOICES], k=1)[0]
    ai_profiles = [
        {
            "title": "AI-driven prompt injection against SOC assistant",
            "category": "ai_prompt_injection",
            "target_asset": "soc-assistant-llm",
            "mitre_tactic": "Collection",
        },
        {
            "title": "AI model poisoning attempt on telemetry classifier",
            "category": "ai_model_poisoning",
            "target_asset": "threat-ml-pipeline",
            "mitre_tactic": "Impact",
        },
        {
            "title": "Synthetic identity deepfake campaign",
            "category": "ai_identity_fraud",
            "target_asset": "iam-control-plane",
            "mitre_tactic": "Initial Access",
        },
    ]
    use_ai_profile = include_ai and random.random() < 0.45
    selected_ai_profile = random.choice(ai_profiles) if use_ai_profile else None
    threat = {
        "id": f"THR-SIM-{random.randint(1000, 9999)}",
        "title": selected_ai_profile["title"] if selected_ai_profile else f"Simulated {sev.title()} event on {tactic}",
        "description": "Synthetic attack generated for cyber range training and live triage drills.",
        "severity": sev,
        "status": "new",
        "category": selected_ai_profile["category"] if selected_ai_profile else random.choice(["malware", "phishing", "lateral_movement", "zero_day"]),
        "source_ip": f"203.0.113.{random.randint(10, 220)}",
        "target_asset": selected_ai_profile["target_asset"] if selected_ai_profile else random.choice(["api-gateway-01", "k8s-node-03", "idp-service-02", "db-primary-01"]),
        "mitre_tactic": selected_ai_profile["mitre_tactic"] if selected_ai_profile else tactic,
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


def run_automation_cycle() -> tuple[bool, bool]:
    attack_injected = False
    map_moved = False
    current_epoch = now_epoch()
    if st.session_state.auto_attack_enabled:
        interval_sec = int(st.session_state.auto_attack_interval_min) * 60
        if current_epoch - st.session_state.last_auto_attack_epoch >= interval_sec:
            inject_simulated_attack(include_ai_driven=st.session_state.auto_attack_include_ai)
            st.session_state.last_auto_attack_epoch = current_epoch
            attack_injected = True

    if st.session_state.auto_move_map and current_epoch - st.session_state.last_auto_move_epoch >= 20:
        moved = move_threat_positions()
        st.session_state.last_auto_move_epoch = current_epoch
        st.session_state.last_map_move_message = f"Auto-move shifted {moved} active threats."
        map_moved = moved > 0
    return attack_injected, map_moved


@st.fragment(run_every="5s")
def render_automation_refresh_driver() -> None:
    if not (st.session_state.auto_attack_enabled or st.session_state.auto_move_map):
        return
    attack_injected, map_moved = run_automation_cycle()
    if st.session_state.auto_attack_enabled:
        interval_sec = int(st.session_state.auto_attack_interval_min) * 60
        elapsed = max(0, int(now_epoch() - st.session_state.last_auto_attack_epoch))
        eta = max(0, interval_sec - elapsed)
        st.caption(f"Live simulation running · next attack ETA: {eta}s")
    else:
        st.caption("Live simulation running.")
    if attack_injected or map_moved:
        st.rerun()


def render_sidebar() -> None:
    with st.sidebar:
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")
        if os.path.exists(logo_path):
            st.image(logo_path, width=170)
        st.caption("SecureX Command SOC Simulator")
        st.write("Live SOC cyber range for interactive analyst training.")
        if st.button("Inject Simulated Attack", use_container_width=True):
            inject_simulated_attack(include_ai_driven=st.session_state.auto_attack_include_ai)
            st.rerun()
        st.markdown("#### Live Attack Intake")
        previous_enabled = st.session_state.auto_attack_enabled
        auto_attack_enabled = st.toggle(
            "Auto incoming attacks",
            key="auto_incoming_attacks_toggle",
        )
        auto_attack_interval_min = st.radio(
            "Attack interval",
            [1, 2],
            horizontal=True,
            key="auto_attack_interval_selector",
        )
        auto_attack_include_ai = st.toggle(
            "Include AI-driven attacks",
            key="include_ai_driven_attacks_toggle",
        )
        st.session_state.auto_attack_enabled = auto_attack_enabled
        st.session_state.auto_attack_interval_min = int(auto_attack_interval_min)
        st.session_state.auto_attack_include_ai = auto_attack_include_ai
        if st.session_state.auto_attack_enabled and not previous_enabled:
            st.session_state.threats = []
            st.session_state.selected_threat_id = None
            inject_simulated_attack(include_ai_driven=st.session_state.auto_attack_include_ai)
            st.session_state.auto_attack_first_wave_pending = False
            st.session_state.last_auto_attack_epoch = now_epoch()
            st.session_state.last_map_move_message = "Auto incoming attacks armed. First alert injected."
            st.rerun()
        if not st.session_state.auto_attack_enabled and previous_enabled:
            st.session_state.auto_attack_first_wave_pending = False


def render_dashboard() -> None:
    inject_css()
    threats = st.session_state.threats
    render_header(threats)
    render_sidebar()
    render_automation_refresh_driver()
    render_stats_bar(threats)
    tab_options = ["Command Overview", "Case Workspace", "Incident Workflow", "Public AI Chat", "MITRE Matrix", "Security Stack"]
    current_tab = st.radio(
        "Workspace",
        tab_options,
        index=tab_options.index(st.session_state.active_dashboard_tab) if st.session_state.active_dashboard_tab in tab_options else 0,
        horizontal=True,
        label_visibility="collapsed",
        key="workspace_tab_selector",
    )
    st.session_state.active_dashboard_tab = current_tab

    if current_tab == "Command Overview":
        left, right = st.columns([1.1, 1.4])
        with left:
            render_feed(threats)
        with right:
            render_geomap(threats)
    elif current_tab == "Case Workspace":
        selected = get_selected_threat()
        render_case_workspace(selected)
    elif current_tab == "Incident Workflow":
        selected = get_selected_threat()
        left, right = st.columns([1.25, 1.0])
        with left:
            render_incident_workflow(selected)
        with right:
            render_kai_panel(selected)
            st.divider()
            render_ranking()
    elif current_tab == "Public AI Chat":
        selected = get_selected_threat()
        render_public_chat(selected)
    elif current_tab == "MITRE Matrix":
        render_attack_matrix(threats)
    elif current_tab == "Security Stack":
        render_stack_topology()


def main() -> None:
    if render_nextjs_bridge():
        return
    ensure_state()
    render_dashboard()


if __name__ == "__main__":
    main()
