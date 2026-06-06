import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Adaptive SOC AI Framework",
    page_icon="🛡️",
    layout="wide",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --soc-bg: #071016;
                --soc-panel: #0f1b24;
                --soc-panel-2: #142330;
                --soc-line: rgba(129, 230, 217, 0.24);
                --soc-text: #e7eef4;
                --soc-muted: #96a9b8;
                --soc-green: #38d689;
                --soc-cyan: #5cc7ff;
                --soc-amber: #f3c969;
                --soc-red: #ff6b6b;
            }

            .stApp {
                background:
                    radial-gradient(circle at 18% 8%, rgba(92, 199, 255, 0.14), transparent 28%),
                    radial-gradient(circle at 82% 4%, rgba(56, 214, 137, 0.12), transparent 26%),
                    linear-gradient(135deg, #071016 0%, #101922 45%, #111827 100%);
                color: var(--soc-text);
            }

            .block-container {
                padding-top: 2rem;
                max-width: 1180px;
            }

            [data-testid="stMetric"] {
                background: rgba(15, 27, 36, 0.76);
                border: 1px solid rgba(150, 169, 184, 0.18);
                border-radius: 8px;
                padding: 1rem;
                min-height: 116px;
            }

            .soc-hero {
                position: relative;
                overflow: hidden;
                border: 1px solid rgba(129, 230, 217, 0.28);
                border-radius: 8px;
                padding: 1.35rem 1.45rem;
                background:
                    linear-gradient(90deg, rgba(15, 27, 36, 0.96), rgba(20, 35, 48, 0.88)),
                    repeating-linear-gradient(0deg, transparent, transparent 28px, rgba(129, 230, 217, 0.07) 29px);
                box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
            }

            .soc-hero::after {
                content: "";
                position: absolute;
                inset: 0;
                background: linear-gradient(90deg, transparent, rgba(92, 199, 255, 0.18), transparent);
                animation: hero-scan 4.8s linear infinite;
                pointer-events: none;
            }

            .soc-kicker {
                color: var(--soc-cyan);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }

            .soc-hero h1 {
                margin: 0.22rem 0 0.35rem;
                color: var(--soc-text);
                font-size: 2.45rem;
                line-height: 1.08;
                letter-spacing: 0;
            }

            .soc-hero p {
                color: var(--soc-muted);
                max-width: 760px;
                margin: 0;
                font-size: 1rem;
            }

            .soc-status-strip {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.8rem;
                margin-top: 1.15rem;
            }

            .soc-status-chip {
                background: rgba(7, 16, 22, 0.72);
                border: 1px solid rgba(150, 169, 184, 0.18);
                border-radius: 8px;
                padding: 0.75rem;
                min-height: 78px;
            }

            .soc-label {
                color: var(--soc-muted);
                font-size: 0.78rem;
            }

            .soc-value {
                color: var(--soc-text);
                font-size: 1.35rem;
                font-weight: 800;
                margin-top: 0.2rem;
            }

            .soc-dot {
                display: inline-block;
                width: 0.58rem;
                height: 0.58rem;
                margin-right: 0.45rem;
                border-radius: 50%;
                background: var(--soc-green);
                box-shadow: 0 0 0 rgba(56, 214, 137, 0.6);
                animation: pulse-dot 1.7s ease-out infinite;
            }

            .soc-section-title {
                margin: 1rem 0 0.65rem;
                color: var(--soc-text);
                font-size: 1.1rem;
                font-weight: 800;
            }

            .pipeline-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.8rem;
            }

            .pipeline-card {
                position: relative;
                overflow: hidden;
                background: linear-gradient(180deg, rgba(20, 35, 48, 0.92), rgba(15, 27, 36, 0.94));
                border: 1px solid rgba(150, 169, 184, 0.18);
                border-radius: 8px;
                padding: 1rem;
                min-height: 128px;
            }

            .pipeline-card::before {
                content: "";
                position: absolute;
                left: 0;
                top: 0;
                height: 3px;
                width: 100%;
                background: linear-gradient(90deg, var(--soc-green), var(--soc-cyan));
                animation: status-flow 3s linear infinite;
            }

            .pipeline-name {
                color: var(--soc-text);
                font-weight: 800;
                margin-bottom: 0.5rem;
            }

            .pipeline-state {
                color: var(--soc-green);
                font-size: 0.9rem;
                font-weight: 700;
            }

            .pipeline-meta {
                color: var(--soc-muted);
                font-size: 0.8rem;
                margin-top: 0.7rem;
            }

            .radar-panel, .feed-panel {
                background: rgba(15, 27, 36, 0.82);
                border: 1px solid rgba(150, 169, 184, 0.18);
                border-radius: 8px;
                padding: 1rem;
                min-height: 310px;
            }

            .radar {
                position: relative;
                width: min(300px, 92vw);
                aspect-ratio: 1;
                margin: 0.5rem auto 0;
                border-radius: 50%;
                border: 1px solid rgba(92, 199, 255, 0.46);
                background:
                    radial-gradient(circle, rgba(56, 214, 137, 0.08) 0 18%, transparent 19%),
                    radial-gradient(circle, transparent 0 34%, rgba(92, 199, 255, 0.14) 35%, transparent 36%),
                    radial-gradient(circle, transparent 0 58%, rgba(92, 199, 255, 0.11) 59%, transparent 60%),
                    linear-gradient(90deg, transparent 49.5%, rgba(92, 199, 255, 0.28) 50%, transparent 50.5%),
                    linear-gradient(0deg, transparent 49.5%, rgba(92, 199, 255, 0.28) 50%, transparent 50.5%);
                box-shadow: inset 0 0 28px rgba(92, 199, 255, 0.16), 0 0 22px rgba(56, 214, 137, 0.1);
            }

            .radar::before {
                content: "";
                position: absolute;
                inset: 50% 0 0 50%;
                background: conic-gradient(from 0deg, rgba(56, 214, 137, 0.42), transparent 58deg);
                transform-origin: 0 0;
                animation: radar-sweep 3.4s linear infinite;
            }

            .radar-blip {
                position: absolute;
                width: 0.7rem;
                height: 0.7rem;
                border-radius: 50%;
                background: var(--soc-amber);
                box-shadow: 0 0 16px rgba(243, 201, 105, 0.75);
                animation: blip 2s ease-in-out infinite;
            }

            .blip-one { left: 64%; top: 28%; }
            .blip-two { left: 34%; top: 60%; animation-delay: 0.6s; background: var(--soc-cyan); }
            .blip-three { left: 72%; top: 70%; animation-delay: 1s; background: var(--soc-green); }

            .feed-row {
                display: grid;
                grid-template-columns: 72px 1fr auto;
                gap: 0.8rem;
                align-items: center;
                padding: 0.72rem 0;
                border-bottom: 1px solid rgba(150, 169, 184, 0.14);
            }

            .feed-time {
                color: var(--soc-cyan);
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                font-size: 0.82rem;
            }

            .feed-text {
                color: var(--soc-text);
                font-size: 0.9rem;
            }

            .feed-tag {
                border: 1px solid rgba(56, 214, 137, 0.28);
                border-radius: 999px;
                color: var(--soc-green);
                font-size: 0.74rem;
                padding: 0.18rem 0.55rem;
                white-space: nowrap;
            }

            .ops-map {
                position: relative;
                overflow: hidden;
                min-height: 420px;
                margin-top: 1rem;
                border: 1px solid rgba(150, 169, 184, 0.18);
                border-radius: 8px;
                background:
                    linear-gradient(90deg, rgba(92, 199, 255, 0.08) 1px, transparent 1px),
                    linear-gradient(0deg, rgba(92, 199, 255, 0.08) 1px, transparent 1px),
                    radial-gradient(circle at 50% 50%, rgba(56, 214, 137, 0.12), transparent 30%),
                    rgba(15, 27, 36, 0.82);
                background-size: 36px 36px, 36px 36px, auto, auto;
            }

            .ops-map::before {
                content: "";
                position: absolute;
                inset: -30%;
                background: conic-gradient(
                    from 120deg,
                    transparent 0deg,
                    rgba(92, 199, 255, 0.08) 45deg,
                    transparent 95deg,
                    rgba(56, 214, 137, 0.1) 150deg,
                    transparent 220deg
                );
                animation: map-drift 18s linear infinite;
            }

            .ops-core {
                position: absolute;
                left: 50%;
                top: 50%;
                z-index: 2;
                width: 190px;
                min-height: 112px;
                transform: translate(-50%, -50%);
                display: grid;
                place-items: center;
                text-align: center;
                border: 1px solid rgba(56, 214, 137, 0.5);
                border-radius: 8px;
                background: rgba(7, 16, 22, 0.9);
                box-shadow: 0 0 34px rgba(56, 214, 137, 0.22);
            }

            .ops-core strong {
                display: block;
                color: var(--soc-text);
                font-size: 1rem;
            }

            .ops-core span {
                color: var(--soc-muted);
                font-size: 0.8rem;
            }

            .ops-ring {
                position: absolute;
                left: 50%;
                top: 50%;
                width: 250px;
                aspect-ratio: 1;
                transform: translate(-50%, -50%);
                border: 1px dashed rgba(92, 199, 255, 0.38);
                border-radius: 50%;
                animation: ring-spin 16s linear infinite;
            }

            .ops-ring.outer {
                width: 340px;
                border-color: rgba(56, 214, 137, 0.24);
                animation-duration: 24s;
                animation-direction: reverse;
            }

            .ops-node {
                position: absolute;
                z-index: 3;
                width: 158px;
                padding: 0.8rem;
                border: 1px solid rgba(150, 169, 184, 0.22);
                border-radius: 8px;
                background: rgba(20, 35, 48, 0.94);
                box-shadow: 0 12px 26px rgba(0, 0, 0, 0.22);
            }

            .ops-node::before {
                content: "";
                position: absolute;
                left: 0.8rem;
                top: 0.8rem;
                width: 0.52rem;
                height: 0.52rem;
                border-radius: 50%;
                background: var(--soc-green);
                box-shadow: 0 0 14px rgba(56, 214, 137, 0.75);
            }

            .ops-node strong {
                display: block;
                color: var(--soc-text);
                font-size: 0.9rem;
                margin-left: 1rem;
            }

            .ops-node span {
                display: block;
                color: var(--soc-muted);
                font-size: 0.76rem;
                margin-top: 0.3rem;
            }

            .node-cloud { left: 5%; top: 18%; }
            .node-endpoint { right: 6%; top: 18%; }
            .node-network { left: 8%; bottom: 16%; }
            .node-container { right: 8%; bottom: 16%; }

            .signal-line {
                position: absolute;
                z-index: 1;
                height: 2px;
                transform-origin: left center;
                background: linear-gradient(90deg, transparent, rgba(92, 199, 255, 0.25), transparent);
            }

            .signal-line::after {
                content: "";
                position: absolute;
                top: -3px;
                left: 0;
                width: 34px;
                height: 8px;
                border-radius: 999px;
                background: rgba(92, 199, 255, 0.82);
                box-shadow: 0 0 18px rgba(92, 199, 255, 0.9);
                animation: signal-travel 2.8s ease-in-out infinite;
            }

            .line-one {
                left: 19%;
                top: 35%;
                width: 31%;
                transform: rotate(20deg);
            }

            .line-two {
                right: 18%;
                top: 34%;
                width: 30%;
                transform: rotate(160deg);
            }

            .line-three {
                left: 19%;
                bottom: 32%;
                width: 31%;
                transform: rotate(-20deg);
            }

            .line-four {
                right: 18%;
                bottom: 32%;
                width: 30%;
                transform: rotate(200deg);
            }

            .line-two::after { animation-delay: 0.4s; }
            .line-three::after { animation-delay: 0.8s; }
            .line-four::after { animation-delay: 1.2s; }

            .flow-grid {
                display: grid;
                grid-template-columns: repeat(5, minmax(0, 1fr));
                gap: 0.7rem;
                margin-top: 1rem;
            }

            .flow-stage {
                position: relative;
                overflow: hidden;
                min-height: 120px;
                padding: 0.95rem;
                border: 1px solid rgba(150, 169, 184, 0.18);
                border-radius: 8px;
                background: linear-gradient(180deg, rgba(20, 35, 48, 0.88), rgba(7, 16, 22, 0.86));
            }

            .flow-stage::after {
                content: "";
                position: absolute;
                left: -45%;
                top: 0;
                width: 42%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(56, 214, 137, 0.16), transparent);
                animation: stage-scan 4s ease-in-out infinite;
            }

            .flow-index {
                color: var(--soc-cyan);
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                font-size: 0.78rem;
            }

            .flow-title {
                color: var(--soc-text);
                font-weight: 800;
                margin-top: 0.35rem;
            }

            .flow-detail {
                color: var(--soc-muted);
                font-size: 0.78rem;
                margin-top: 0.45rem;
            }

            .flow-stage:nth-child(2)::after { animation-delay: 0.4s; }
            .flow-stage:nth-child(3)::after { animation-delay: 0.8s; }
            .flow-stage:nth-child(4)::after { animation-delay: 1.2s; }
            .flow-stage:nth-child(5)::after { animation-delay: 1.6s; }

            @keyframes hero-scan {
                0% { transform: translateX(-120%); }
                100% { transform: translateX(120%); }
            }

            @keyframes pulse-dot {
                0% { box-shadow: 0 0 0 0 rgba(56, 214, 137, 0.58); }
                70% { box-shadow: 0 0 0 12px rgba(56, 214, 137, 0); }
                100% { box-shadow: 0 0 0 0 rgba(56, 214, 137, 0); }
            }

            @keyframes status-flow {
                0% { filter: hue-rotate(0deg); }
                100% { filter: hue-rotate(80deg); }
            }

            @keyframes radar-sweep {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            @keyframes blip {
                0%, 100% { transform: scale(0.82); opacity: 0.55; }
                50% { transform: scale(1.15); opacity: 1; }
            }

            @keyframes map-drift {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            @keyframes ring-spin {
                from { transform: translate(-50%, -50%) rotate(0deg); }
                to { transform: translate(-50%, -50%) rotate(360deg); }
            }

            @keyframes signal-travel {
                0% { transform: translateX(0); opacity: 0; }
                15% { opacity: 1; }
                80% { opacity: 1; }
                100% { transform: translateX(260px); opacity: 0; }
            }

            @keyframes stage-scan {
                0% { transform: translateX(0); opacity: 0; }
                18% { opacity: 1; }
                75% { opacity: 1; }
                100% { transform: translateX(340%); opacity: 0; }
            }

            @media (max-width: 900px) {
                .soc-status-strip, .pipeline-grid, .flow-grid {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }

                .soc-hero h1 {
                    font-size: 1.9rem;
                }

                .ops-map {
                    min-height: 640px;
                }

                .ops-core {
                    top: 50%;
                }

                .node-cloud, .node-endpoint, .node-network, .node-container {
                    left: 50%;
                    right: auto;
                    transform: translateX(-50%);
                }

                .node-cloud { top: 5%; }
                .node-endpoint { top: 24%; }
                .node-network { bottom: 24%; }
                .node-container { bottom: 5%; }

                .signal-line {
                    display: none;
                }
            }

            @media (max-width: 560px) {
                .soc-status-strip, .pipeline-grid, .flow-grid {
                    grid-template-columns: 1fr;
                }

                .feed-row {
                    grid-template-columns: 1fr;
                    gap: 0.25rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
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


def get_security_events_data() -> list[dict[str, str]]:
    # Placeholder for future Docker service API integration.
    return [
        {
            "Time": "09:41",
            "Event": "Kubernetes CI passed manifest linting and overlay validation",
            "Status": "Verified",
        },
        {
            "Time": "09:44",
            "Event": "Suricata network anomaly routed to triage queue",
            "Status": "Triaged",
        },
        {
            "Time": "09:47",
            "Event": "LimaCharlie endpoint observation correlated with baseline",
            "Status": "Observed",
        },
        {
            "Time": "09:51",
            "Event": "Docker service health probe remained stable",
            "Status": "Healthy",
        },
    ]


def get_pipeline_status_data() -> pd.DataFrame:
    # Placeholder for future Docker service API integration.
    return pd.DataFrame(
        [
            {
                "Pipeline": "Terraform CI",
                "Status": "Pass",
                "Detail": "Foundation validated",
            },
            {
                "Pipeline": "Ansible CI",
                "Status": "Pass",
                "Detail": "Inventory checks green",
            },
            {
                "Pipeline": "Docker CI",
                "Status": "Pass",
                "Detail": "Service build verified",
            },
            {
                "Pipeline": "Kubernetes CI",
                "Status": "Pass",
                "Detail": "Kustomize overlays passed",
            },
        ]
    )


def render_header() -> None:
    st.markdown(
        """
        <section class="soc-hero">
            <div class="soc-kicker"><span class="soc-dot"></span>Live demo operations view</div>
            <h1>Adaptive SOC AI Framework</h1>
            <p>
                Infrastructure, automation, containers, and Kubernetes validation are now
                presented as one recruiter-friendly SOC command surface.
            </p>
            <div class="soc-status-strip">
                <div class="soc-status-chip">
                    <div class="soc-label">Framework Stage</div>
                    <div class="soc-value">Kubernetes CI</div>
                </div>
                <div class="soc-status-chip">
                    <div class="soc-label">Validation State</div>
                    <div class="soc-value">Passed</div>
                </div>
                <div class="soc-status-chip">
                    <div class="soc-label">Environments</div>
                    <div class="soc-value">3 overlays</div>
                </div>
                <div class="soc-status-chip">
                    <div class="soc-label">SOC Mode</div>
                    <div class="soc-value">Monitoring</div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


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
    pipelines = get_pipeline_status_data()
    cards = []
    for row in pipelines.to_dict("records"):
        cards.append(
            f"""
            <div class="pipeline-card">
                <div class="pipeline-name">{row["Pipeline"]}</div>
                <div class="pipeline-state"><span class="soc-dot"></span>{row["Status"]}</div>
                <div class="pipeline-meta">{row["Detail"]}</div>
            </div>
            """
        )
    st.markdown('<div class="soc-section-title">Pipeline Status</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="pipeline-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )


def render_operations_map() -> None:
    st.markdown(
        """
        <div class="soc-section-title">Adaptive SOC Operations Map</div>
        <div class="ops-map">
            <div class="ops-ring"></div>
            <div class="ops-ring outer"></div>
            <div class="signal-line line-one"></div>
            <div class="signal-line line-two"></div>
            <div class="signal-line line-three"></div>
            <div class="signal-line line-four"></div>
            <div class="ops-core">
                <div>
                    <strong>AI SOC Control Plane</strong>
                    <span>correlate - validate - respond</span>
                </div>
            </div>
            <div class="ops-node node-cloud">
                <strong>Cloud</strong>
                <span>Terraform foundation and AWS guardrails</span>
            </div>
            <div class="ops-node node-endpoint">
                <strong>Endpoint</strong>
                <span>LimaCharlie-style telemetry stream</span>
            </div>
            <div class="ops-node node-network">
                <strong>Network</strong>
                <span>Suricata anomaly signals and triage</span>
            </div>
            <div class="ops-node node-container">
                <strong>Kubernetes</strong>
                <span>Validated overlays and service runtime</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_incident_flow() -> None:
    stages = [
        ("01", "Ingest", "Signals enter from cloud, network, endpoint, and container layers."),
        ("02", "Normalize", "Events become shared SOC records with framework context."),
        ("03", "Correlate", "Related signals are grouped into an investigation path."),
        ("04", "Validate", "CI, controls, and health checks confirm deployment posture."),
        ("05", "Respond", "The operator gets a clear next action and confidence state."),
    ]
    stage_markup = []
    for index, title, detail in stages:
        stage_markup.append(
            f"""
            <div class="flow-stage">
                <div class="flow-index">{index}</div>
                <div class="flow-title">{title}</div>
                <div class="flow-detail">{detail}</div>
            </div>
            """
        )

    st.markdown('<div class="soc-section-title">Signal Processing Flow</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="flow-grid">{"".join(stage_markup)}</div>',
        unsafe_allow_html=True,
    )


def render_radar() -> None:
    st.markdown(
        """
        <div class="radar-panel">
            <div class="soc-section-title">Security Signal Radar</div>
            <div class="radar">
                <span class="radar-blip blip-one"></span>
                <span class="radar-blip blip-two"></span>
                <span class="radar-blip blip-three"></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_security_feed() -> None:
    rows = []
    for event in get_security_events_data():
        rows.append(
            f"""
            <div class="feed-row">
                <div class="feed-time">{event["Time"]}</div>
                <div class="feed-text">{event["Event"]}</div>
                <div class="feed-tag">{event["Status"]}</div>
            </div>
            """
        )
    st.markdown(
        f"""
        <div class="feed-panel">
            <div class="soc-section-title">Live Validation Feed</div>
            {"".join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    apply_theme()
    render_header()
    st.divider()
    render_pipeline_status()
    render_operations_map()
    render_incident_flow()
    st.divider()

    top_left, top_right = st.columns((1, 1))

    with top_left:
        render_radar()

    with top_right:
        render_security_feed()

    st.divider()
    render_system_health()
    render_active_threats()


if __name__ == "__main__":
    main()
