import pandas as pd
import streamlit as st
import random
import base64
import os
import pydeck as pdk
import json
from urllib.request import urlopen
from datetime import datetime
import time
import google.generativeai as genai


st.set_page_config(
    page_title="Adaptive SOC AI Framework",
    page_icon="🛡️",
    layout="wide",
)


def inject_custom_css(breach_active: bool = False) -> None:
    alert_style = '.stApp { animation: alert-flash 1.5s infinite !important; } @keyframes alert-flash { 0%, 100% { background-color: #000000; } 50% { background-color: #001a00; } }' if breach_active else ''
    ai_breach_style = '.ai-analyst-box { border: 2px solid #00FF00 !important; box-shadow: 0 0 30px rgba(0, 255, 0, 0.2) !important; transform: scale(1.02); transition: all 0.5s ease; }' if breach_active else ''
    map_flash = '.map-container { animation: map-pulse-border 1s infinite !important; border: 2px solid #00FF00 !important; } @keyframes map-pulse-border { 0%, 100% { box-shadow: 0 0 5px #00FF00; } 50% { box-shadow: 0 0 25px #00FF00; } }' if breach_active else ''
    spin_speed = "5s" if breach_active else "20s"
    st.markdown("""
        <style>
        /* Sovereign Canvas Reset & Corporate Depth */
        .stApp {
            background: 
                radial-gradient(circle at 50% 50%, #0a1118 0%, #000000 100%) !important;
            background-attachment: fixed !important;
            color: #FFFFFF !important;
        }
        [data-testid="stSidebar"] {
            background-color: rgba(5, 8, 12, 0.8) !important;
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(0, 255, 0, 0.1) !important;
        }
        [data-testid="stSidebar"] label p {
            color: #FFFFFF !important;
            font-family: 'Courier New', monospace !important;
        }
        /* Splunk/Chronicle Tactical Terminal */
        .analyst-terminal {
            background: rgba(0, 10, 0, 0.95);
            border: 1px solid #00FF00;
            padding: 15px;
            font-family: 'Courier New', monospace;
            color: #00FF00;
            height: 350px;
            overflow-y: auto;
            margin-bottom: 20px;
            box-shadow: inset 0 0 15px rgba(0, 255, 0, 0.2);
        }
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                linear-gradient(rgba(0, 255, 0, 0.015) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 0, 0.015) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
            z-index: 0;
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

        /* Kinetic Globe Projection Control */
        .globe-texture { 
            animation: globe-spin """ + spin_speed + """ linear infinite !important; 
            opacity: 0.4; 
        }
        @keyframes globe-spin { 
            0% { transform: translateX(0); } 100% { transform: translateX(-400px); } 
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
            background: rgba(10, 15, 24, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 255, 0, 0.1);
            border-left: 4px solid #00FF00;
            padding: 15px;
            margin-top: 20px; /* Ensure sufficient spacing from other elements */
        }
        
        /* High-Density Command Metric Containers */
        .pipeline-card {
            background: rgba(5, 5, 5, 0.6);
            backdrop-filter: blur(5px);
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.05);
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
            background-color: rgba(0, 0, 0, 0.4) !important;
            border: 1px solid rgba(0, 255, 0, 0.05) !important;
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
        /* Mobile-First Responsive Overrides */
        @media (max-width: 768px) {
            .header-container { flex-direction: column !important; align-items: center !important; text-align: center !important; gap: 25px !important; width: 100% !important; }
            .logo-img { margin-right: 0 !important; margin-bottom: 15px !important; height: 90px !important; max-width: 100% !important; }
            .header-metrics { flex-direction: column !important; gap: 20px !important; align-items: center !important; width: 100% !important; justify-content: center !important; }
            .header-metrics > div { text-align: center !important; margin: 0 auto !important; }
            .ai-content-wrapper { flex-direction: column !important; gap: 25px !important; }
            .risk-score-box { width: 100% !important; border-left: none !important; border-top: 1px solid rgba(0, 255, 0, 0.2) !important; padding: 20px 0 0 0 !important; }
            .stMetric { width: 100% !important; }
            .map-container { height: 400px !important; }
        }
        /* Breach Simulation Overlay */
        """ + alert_style + """
        """ + ai_breach_style + """
        """ + map_flash + """
        </style>
    """, unsafe_allow_html=True)


def get_ai_engine_metrics() -> dict:
    """Provides tactical telemetry for the AI Charlie SLM Engine."""
    return {
        "inference_ms": random.randint(45, 120),
        "model_confidence": f"{random.uniform(94.2, 99.8):.1f}%",
        "neural_link": "STABLE"
    }


def get_active_threats_data() -> pd.DataFrame:
    # Protocol: Check for local telemetry file ingestion
    telemetry_path = os.path.join(os.path.dirname(__file__), "telemetry.json")
    local_data = []
    if os.path.exists(telemetry_path):
        try:
            with open(telemetry_path, "r") as f:
                local_data = json.load(f)
        except Exception:
            pass

    threat_pool = [
        {
            "ID": "TR-1001", "Severity": "Low", "Source": "Edge-Sec", "Vector": "Phishing Attempt", "Status": "Active", "lat": 34.0522, "lon": -118.2437, "MITRE": "T1566.001", "CVE": "N/A",
            "Playbook": ["Block Sender", "Quarantine Mail", "Ignore"], "Correct": "Quarantine Mail", 
            "DistractorExplanations": {"Block Sender": "Insufficient. The payload is already in the inbox.", "Ignore": "High risk of credential theft."},
            "Hint": "Isolate the delivery vector immediately.",
            "Steps": ["1. Purge mail from all inboxes", "2. Block sender domain at gateway", "3. Force password reset for recipient."],
            "Insight": "Entry-level phishing simulation: suspicious .zip link detected in HR mail queue."
        },
        {
            "ID": "TR-1002", "Severity": "Medium", "Source": "Intra-Probe", "Vector": "Internal Network Scan", "Status": "Active", "lat": 35.6762, "lon": -139.6503, "MITRE": "T1046", "CVE": "N/A", 
            "Playbook": ["Disable Port", "Quarantine Host", "Audit Logs"], "Correct": "Quarantine Host",
            "DistractorExplanations": {"Disable Port": "Too narrow. Attacker will switch ports.", "Audit Logs": "Good for forensics, but doesn't stop the live scan."},
            "Hint": "Stop the reconnaissance phase by isolating the source machine.",
            "Steps": ["1. Move host to isolation VLAN", "2. Terminate scanning process", "3. Snapshot disk for analysis."],
            "Insight": "Intermediate scan detected. Unauthorized Nmap activity from developer workstation."
        },
        {
            "ID": "TR-1081", "Severity": "Critical", "Source": "Suricata", "Vector": "Log4Shell RCE", "Status": "Active", "lat": 51.5074, "lon": -0.1278, "MITRE": "T1190", "CVE": "CVE-2021-44228", 
            "Playbook": ["Disable JNDI", "Patch Log4j", "WAF Filter"], "Correct": "Patch Log4j", 
            "DistractorExplanations": {"Disable JNDI": "Suboptimal. The library remains on disk and can be bypassed.", "WAF Filter": "Ineffective against nested polymorphic lookups."},
            "Hint": "Look for the remediation that targets the library version itself.",
            "Steps": ["1. Identify vulnerable JARs", "2. Update to Log4j 2.17+", "3. Restart JVM."],
            "Insight": "Polymorphic payload detected. Obfuscated strings observed bypassing EDR."
        },
        {
            "ID": "TR-1084", "Severity": "Critical", "Source": "Darktrace", "Vector": "MOVEit Transfer Exfil", "Status": "Active", "lat": 40.7128, "lon": -74.0060, "MITRE": "T1190", "CVE": "CVE-2023-34362", 
            "Playbook": ["Disable SFTP", "Rotate DB Keys", "IP Blocklist"], "Correct": "IP Blocklist",
            "DistractorExplanations": {"Disable SFTP": "Too slow. Data is already leaving via HTTPS.", "Rotate DB Keys": "Doesn't stop the current exfiltration stream."},
            "Hint": "We need an immediate network block on the egress destination.",
            "Steps": ["1. Block Source IP at Firewall", "2. Quarantining File Server", "3. Audit SFTP Logs."],
            "Insight": "Zero-day SQL injection in progress. High-volume data exfiltration detected."
        },
        {
            "ID": "TR-1089", "Severity": "Critical", "Source": "GuardDuty", "Vector": "Citrix Bleed", "Status": "Active", "lat": 1.3521, "lon": 103.8198, "MITRE": "T1190", "CVE": "CVE-2023-4966", 
            "Playbook": ["Clear Sessions", "Update NetScaler", "Kill Active VPN"], "Correct": "Update NetScaler",
            "DistractorExplanations": {"Clear Sessions": "Temporary. The exploit can be re-run immediately.", "Kill Active VPN": "Does not address the vulnerability in the NetScaler appliance."},
            "Hint": "The vulnerability lies in the appliance memory handling.",
            "Steps": ["1. Apply NetScaler firmware patch", "2. Force password reset", "3. Clear all active sessions."],
            "Insight": "Information disclosure vulnerability allowing session hijacking without credentials."
        }
    ]
    
    if 'threat_log' not in st.session_state:
        st.session_state.threat_log = []
    return pd.DataFrame(local_data + threat_pool)


def get_pipeline_status_data() -> pd.DataFrame:
    return pd.DataFrame([
        {"Pipeline": "Terraform Engine", "Status": "ACTIVE"},
        {"Pipeline": "Ansible Automation", "Status": "ACTIVE"},
        {"Pipeline": "Docker Runtime", "Status": "ACTIVE"},
        {"Pipeline": "Kubernetes Cluster", "Status": "ACTIVE"}
    ])


@st.cache_data
def get_base64_logo(file_path: str) -> str:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def render_header(threat_count: int, assets_count: int) -> None:
    logo_path = os.path.join(os.path.dirname(__file__), "securex.png")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")
    
    logo_b64 = get_base64_logo(logo_path)
    logo_html = f'<img class="logo-img" src="data:image/png;base64,{logo_b64}" style="height:150px;margin-right:25px;vertical-align:middle;filter:drop-shadow(0 0 15px #00FF00);">' if logo_b64 else ""
    
    header_html = f'<div class="header-container" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;margin-bottom:30px;border-bottom:1px solid #1A1A1A;padding-bottom:20px;width:100%;"><div style="display:flex;align-items:center;flex-wrap:wrap;justify-content:center;">{logo_html}<div><h1 style="margin:0;font-family:\'Courier New\',monospace;font-size:2.2rem;font-weight:900;letter-spacing:4px;color:#00FF00;">SECUREX COMMAND</h1><p style="color:#FFFFFF;margin:5px 0 0 0;font-size:0.85rem;letter-spacing:1px;">[ SYSTEM INFRASTRUCTURE MONITORING V1.0 ]</p></div></div><div class="header-metrics" style="display:flex;gap:40px;align-items:center;flex-wrap:wrap;justify-content:center;"><div style="text-align:right;"><div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">THREATS TODAY</div><div style="color:#00FF00;font-weight:bold;font-size:1.2rem;">{threat_count}</div></div><div style="text-align:right;"><div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">ASSETS MONITORED</div><div style="color:#FFFFFF;font-weight:bold;font-size:1.2rem;">{assets_count:,}</div></div><div style="background:#000000;border:1px solid #00FF00;padding:8px 15px;"><span class="status-pulse-commander"></span><span style="color:#00FF00;font-weight:bold;font-size:0.8rem;letter-spacing:2px;font-family:\'Courier New\',monospace;">COMMAND CENTER ACTIVE</span></div></div></div>'
    st.markdown(header_html, unsafe_allow_html=True)


def render_ai_engine_telemetry() -> None:
    ai_stats = get_ai_engine_metrics()
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// AI ANALYST ENGINE TELEMETRY</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Inference Latency", f"{ai_stats['inference_ms']}ms")
    c2.metric("Model Confidence", ai_stats['model_confidence'])
    c3.metric("Neural Link", ai_stats['neural_link'])


def render_active_threats() -> None:
    threat_list = st.session_state.get('threat_log', [])
    threats = pd.DataFrame(threat_list)
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// LIVE THREAT FEED</p>", unsafe_allow_html=True)
    if threats.empty:
        st.markdown("<p style='color: #777777; font-size: 0.8rem;'>ALL THREATS NEUTRALIZED. SECTOR CLEAR.</p>", unsafe_allow_html=True)
        return
    for _, row in threats.iterrows():
        severity_color = {"Critical": "#00FF00", "High": "#FFFFFF", "Medium": "#777777", "Low": "#444444"}.get(row["Severity"], "#222222")
        threat_html = f'<div style="margin-bottom:12px;border-left:2px solid {severity_color};padding-left:10px;"><div style="font-size:0.75rem;color:#FFFFFF;">[{row["Time"]}] <span style="color:{severity_color};">{row["Source"]}</span></div><div style="font-size:0.8rem;color:#FFFFFF;font-weight:bold;">{row["Vector"]}</div><div style="font-size:0.7rem;color:#00FF00;margin-top:2px;font-family:\'Courier New\',monospace;"><a href="https://attack.mitre.org/techniques/{row.get("MITRE", "")}/" target="_blank" style="color:#00FF00;text-decoration:none;">{row.get("MITRE", "")}</a> | <a href="https://nvd.nist.gov/vuln/detail/{row.get("CVE", "")}" target="_blank" style="color:#00FF00;text-decoration:none;">{row.get("CVE", "")}</a></div></div>'
        st.markdown(threat_html, unsafe_allow_html=True)


def render_anomaly_map(zoom_lat=None, zoom_lon=None) -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// LIVE GEOSPATIAL TELEMETRY [ SATELLITE MODE ]</p>", unsafe_allow_html=True)

    # Determine "Home" location
    try:
        url = 'http://ip-api.com/json'
        response = urlopen(url)
        data = json.load(response)
        curr_lat, curr_lon = data['lat'], data['lon']
    except:
        curr_lat, curr_lon = 51.5074, -0.1278 # Falls back to London

    threats = pd.DataFrame(st.session_state.get('threat_log', []))
    
    # Determine View State based on attack
    view_lat = zoom_lat if zoom_lat else curr_lat
    view_lon = zoom_lon if zoom_lon else curr_lon
    zoom_level = 10 if zoom_lat else 2

    # Create arcs for movement
    if not threats.empty:
        threats['target_lat'] = curr_lat
        threats['target_lon'] = curr_lon
    
    scatterplot = pdk.Layer(
        "ScatterplotLayer",
        threats,
        get_position=["lon", "lat"],
        get_color="[0, 255, 0, 160]",
        get_radius=150000,
        pickable=True
    )

    arclayer = pdk.Layer(
        "ArcLayer",
        threats,
        get_source_position=["lon", "lat"],
        get_target_position=["target_lon", "target_lat"],
        get_source_color=[0, 255, 0, 80],
        get_target_color=[0, 255, 0, 255],
        get_width=3,
        animation_speed=2,
    )
    
    view_state = pdk.ViewState(
        latitude=view_lat,
        longitude=view_lon,
        zoom=zoom_level,
        pitch=45,
    )
    
    r = pdk.Deck(
        layers=[arclayer, scatterplot],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/satellite-streets-v11",
        tooltip={"text": "Anomaly: {Vector}\nSource: {Source}"}
    )
    
    st.pydeck_chart(r)


def ask_ai_charlie(query, threat_context=None):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            return "AI Charlie's neural link is offline. (Missing API Key)"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        context_prompt = f"You are AI Charlie, an expert SOC Analyst mentor. Help the student understand this security event: {threat_context}. " if threat_context else "You are AI Charlie, a SOC mentor."
        full_prompt = f"{context_prompt} User asks: {query}. Keep it tactical, technical, and educational. Reference MITRE or NIST if applicable."
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Neural Link Error: {str(e)}"


def render_ai_analyst() -> None:
    ranks = [
        "TIER 1 (ASSOCIATE ANALYST)", 
        "TIER 2 (INCIDENT RESPONDER)", 
        "TIER 3 (SENIOR INVESTIGATOR)", 
        "THREAT HUNTER (PROFESSIONAL)", 
        "INCIDENT COMMANDER (EXPERT)", 
        "SOC ARCHITECT (MASTER)", 
        "OFFICERS CLUB (SME)"
    ]
    points = st.session_state.get('points', 0)
    current_rank = ranks[min(points // 20, len(ranks)-1)]

    threat_list = st.session_state.get('threat_log', [])
    if not threat_list or not isinstance(threat_list[0], dict):
        st.sidebar.markdown('<div class="analyst-terminal">> SYSTEM SECURE.<br>> NO ACTIVE THREATS.</div>', unsafe_allow_html=True)
        return

    latest = threat_list[0]
    intel_text = ""
    if st.session_state.show_intel:
        intel_text = f"<br><br>> AI CHARLIE: Accessing high-authority intel channels...<br>> - <a href='https://attack.mitre.org/techniques/{latest.get('MITRE','')}/' target='_blank' style='color:#00FF00;'>MITRE: {latest.get('MITRE','')}</a><br>> - <a href='https://nvd.nist.gov/vuln/detail/{latest.get('CVE','')}' target='_blank' style='color:#00FF00;'>NIST: {latest.get('CVE','')}</a>"
    
    # Manage chat window inside terminal
    chat_display = ""
    for chat in st.session_state.chat_history[-2:]: # Show last 2 exchanges
        chat_display += f"<br>> 👤 Student: {chat['user']}<br>> 🤖 Charlie: {chat['ai']}<br>"

    hint_text = f"<br><br>> [HINT]: {latest.get('Hint')}" if st.session_state.show_hint else ""
    error_text = f"<br><br><span style='color:#FF4B4B;'>[ERROR]: {st.session_state.last_error}</span>" if st.session_state.last_error else ""

    st.sidebar.markdown(f"""
    <div class="analyst-terminal">
        > ACCESSING AI CHARLIE ANALYST...<br>
        > RANK: {current_rank}<br>
        > SCORE: {st.session_state.points} XP<br>
        -------------------------<br>
        > 🤖 AI CHARLIE: Commander, {latest.get('Vector', 'Unknown Vector')} detected.<br><br>
        > LOG: "{latest.get('Insight')}"{intel_text}{hint_text}{error_text}{chat_display}<br><br>
        > ADVISORY: Ask me anything or execute protocol.
    </div>
    """, unsafe_allow_html=True)

    # Student Chat Input
    user_query = st.sidebar.text_input("Ask Charlie for help:", key="ai_chat_input")
    if user_query:
        with st.sidebar:
            with st.spinner("Analyzing..."):
                ai_resp = ask_ai_charlie(user_query, latest.get('Vector'))
                st.session_state.chat_history.append({"user": user_query, "ai": ai_resp})
                st.rerun()

    c1, c2 = st.sidebar.columns(2)
    if c1.button("📡 INTEL", key="intel_btn", use_container_width=True):
        st.session_state.show_intel = not st.session_state.show_intel; st.rerun()
    if c2.button("💡 HINT", key="hint_btn", use_container_width=True):
        st.session_state.show_hint = not st.session_state.show_hint; st.rerun()

    for action in latest.get('Playbook', []):
        if st.sidebar.button(f"EXECUTE: {action}", key=f"act_{latest['ID']}_{action}", use_container_width=True):
            if action == latest.get('Correct'):
                st.balloons()
                st.session_state.points += 10
                st.session_state.threat_log.pop(0)
                st.session_state.show_intel = False; st.session_state.show_hint = False; st.session_state.last_error = ""
                st.session_state.threat_count += 0 # Keep total count but refresh display
                st.session_state.assets_count += random.randint(1, 10) # Discovery XP
                steps_list = latest.get('Steps', [])
                steps = "\n".join(steps_list) if isinstance(steps_list, list) else "Steps not documented."
                st.sidebar.success(f"CORRECT.\n\nFIELD STEPS:\n{steps}")
                st.rerun()
            else:
                st.session_state.last_error = latest.get('DistractorExplanations', {}).get(action, "Incorrect protocol selection.")
                st.rerun()


def render_incident_ledger() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 30px 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// MASTER INCIDENT LEDGER</p>", unsafe_allow_html=True)
    threat_list = st.session_state.get('threat_log', [])
    
    if not threat_list:
        st.markdown("<p style='color: #444444; font-size: 0.8rem; font-family: monospace;'>[SYSTEM MESSAGE]: LEDGER EMPTY. NO CURRENT INCIDENTS RECORDED.</p>", unsafe_allow_html=True)
        return

    table_rows = ""
    for t in threat_list:
        color = "#444444"
        sev = t.get("Severity", "Low")
        if sev == "Critical": color = "#00FF00"
        elif sev == "High": color = "#FFFFFF"
        elif sev == "Medium": color = "#777777"

        table_rows += f"""
        <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); font-family: monospace;">
            <td style="padding: 12px; color: #777777;">{t.get('Time')}</td>
            <td style="padding: 12px; font-weight: bold; color: {color};">{sev.upper()}</td>
            <td style="padding: 12px; color: #FFFFFF;">{t.get('ID')}</td>
            <td style="padding: 12px; color: #FFFFFF;">{t.get('Vector')}</td>
            <td style="padding: 12px; color: #777777;">{t.get('MITRE')}</td>
            <td style="padding: 12px; color: #00FF00; font-weight: bold;">{t.get('Status')}</td>
        </tr>"""

    ledger_html = f"""
    <div style="background: rgba(10, 15, 24, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; width: 100%; overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; font-size: 0.75rem; text-align: left;">
            <thead style="background: rgba(0, 255, 0, 0.03); border-bottom: 1px solid rgba(0, 255, 0, 0.2);">
                <tr><th style="padding: 12px; color: #00FF00;">TIMESTAMP</th><th style="padding: 12px; color: #00FF00;">SEVERITY</th><th style="padding: 12px; color: #00FF00;">INCIDENT_ID</th><th style="padding: 12px; color: #00FF00;">ATTACK_VECTOR</th><th style="padding: 12px; color: #00FF00;">MITRE_REF</th><th style="padding: 12px; color: #00FF00;">OPS_STATUS</th></tr>
            </thead>
            <tbody>{table_rows}</tbody>
        </table>
    </div>"""
    st.markdown(ledger_html, unsafe_allow_html=True)


def render_pipeline_status() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// AUTOMATION HEALTH</p>", unsafe_allow_html=True)
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        card_html = f'<div class="pipeline-card"><div class="pipeline-name">{row["Pipeline"]}</div><div style="color:#00FF00;font-size:0.75rem;font-weight:bold;margin-top:4px;">● SECURE</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)


def main() -> None:
    # Sovereign Initialization: Must execute before any UI calls to prevent crashes
    session_defaults = {
        'threat_log': [],
        'threat_count': 0,
        'assets_count': 0,
        'points': 0,
        'prev_rank_idx': 0,
        'last_error': "",
        'last_auto_injection': time.time(),
        'show_intel_feed': False,
        'chat_history': [],
        'show_intel': False,
        'show_hint': False,
        'next_interval': 10,
        'auto_step': 0,
        'breach_sim_active': False
    }
    
    for key, val in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    with st.sidebar:
        st.markdown("<p style='color: #FFFFFF; font-size: 0.7rem; letter-spacing: 1px;'>// TACTICAL SIMULATION</p>", unsafe_allow_html=True)
        breach_sim = st.toggle("SIMULATE SYSTEM BREACH", value=False)

        # Handle Toggle Reset Logic
        if breach_sim and not st.session_state.breach_sim_active:
            st.session_state.last_auto_injection = time.time()
            st.session_state.next_interval = 10
            st.session_state.auto_step = 0
            st.session_state.breach_sim_active = True
        elif not breach_sim:
            st.session_state.breach_sim_active = False

        # Real-Time Countdown Engine
        if breach_sim:
            current_time = time.time()
            elapsed = current_time - st.session_state.last_auto_injection
            remaining = max(0, int(st.session_state.next_interval - elapsed))
            mins, secs = divmod(remaining, 60)
            
            countdown_html = f'<div style="border:1px solid #00FF00;padding:10px;margin-bottom:20px;text-align:center;background:rgba(0,255,0,0.05);"><span style="color:#00FF00;font-size:0.65rem;letter-spacing:1px;">T-MINUS NEXT BREACH</span><br><span style="color:#FFFFFF;font-size:1.4rem;font-family:monospace;">{mins:02d}:{secs:02d}</span></div>'
            st.markdown(countdown_html, unsafe_allow_html=True)

            if elapsed >= st.session_state.next_interval:
                pool = get_active_threats_data()
                
                # Severity Progression Logic
                if st.session_state.auto_step == 0:
                    candidates = pool[pool['Severity'] == 'Low']
                elif st.session_state.auto_step == 1:
                    candidates = pool[pool['Severity'] == 'Medium']
                else:
                    candidates = pool[pool['Severity'].isin(['High', 'Critical'])]
                
                if candidates.empty: candidates = pool
                
                new_threat = candidates.sample(1).to_dict('records')[0].copy()
                new_threat["ID"] = f"TR-AUTO-{random.randint(1000, 9999)}"
                new_threat["Time"] = datetime.now().strftime("%H:%M:%S")
                st.session_state.threat_log = [new_threat] + st.session_state.threat_log[:9]
                st.session_state.threat_count += 1
                st.session_state.assets_count += random.randint(10, 100)
                st.session_state.last_auto_injection = current_time
                st.session_state.next_interval = 60
                st.session_state.auto_step += 1
                st.rerun()

        st.session_state.show_intel_feed = st.checkbox("OPEN SIEM INTELLIGENCE FEED", value=st.session_state.show_intel_feed)

        if st.button("INJECT DETECTION EVENT"):
            new_threat = random.choice(get_active_threats_data().to_dict('records')).copy()
            new_threat["ID"] = f"TR-{random.randint(2000, 9999)}"
            new_threat["Time"] = datetime.now().strftime("%H:%M:%S")
            # Prepend to keep latest on top
            st.session_state.threat_log = [new_threat] + st.session_state.threat_log[:9]
            st.session_state.threat_count += 1
            st.session_state.assets_count += random.randint(5, 50)
            st.rerun()

        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.1);padding-top:10px;'><p style='color: #555555; font-size: 0.6rem; line-height: 1.2;'>// GDPR COMPLIANCE: THIS SYSTEM PROCESSES TEMPORARY IP DATA FOR GEOSPATIAL PROJECTION. DATA IS VOLATILE AND NOT PERSISTED BEYOND THE ACTIVE SESSION. [ FRAMEWORK VERSION 1.0 ]</p></div>", unsafe_allow_html=True)

    # TACTICAL ENGINE: Automatic Breach Trigger Logic
    threat_list = st.session_state.get('threat_log', [])
    latest_critical = next((t for t in threat_list if t.get("Severity") == "Critical"), None)
    active_breach_mode = breach_sim or (latest_critical is not None)

    inject_custom_css(breach_active=active_breach_mode)
    render_header(st.session_state.threat_count, st.session_state.assets_count)

    # SIEM Intelligence Window Overlay
    if st.session_state.get('show_intel_feed') and threat_list:
        latest = threat_list[0]
        st.markdown(f"""
            <div style="background: rgba(0, 40, 0, 0.85); border: 2px solid #00FF00; padding: 20px; border-radius: 5px; margin-bottom: 25px; backdrop-filter: blur(10px);">
                <h3 style="color: #00FF00; margin: 0 0 10px 0;">📡 SIEM INTELLIGENCE FEED: {latest.get('ID')}</h3>
                <p style="color: #FFFFFF; font-size: 0.9rem;"><b>Vector:</b> {latest.get('Vector')} | <b>Source:</b> {latest.get('Source')} | <b>Status:</b> {latest.get('Status')}</p>
                <p style="color: #AAAAAA; font-size: 0.85rem; border-top: 1px solid rgba(0,255,0,0.2); padding-top: 10px;">{latest.get('Insight')}</p>
            </div>
        """, unsafe_allow_html=True)

    # Dynamic Map Zoom based on latest Critical Threat
    map_lat, map_lon = None, None
    if active_breach_mode and latest_critical:
        map_lat, map_lon = latest_critical['lat'], latest_critical['lon']
    
    # Main Command Deck
    col_left, col_center, col_right = st.columns([1.2, 4, 1.2])
    
    with col_left:
        render_active_threats()
        
    with col_center:
        render_anomaly_map(zoom_lat=map_lat, zoom_lon=map_lon)
        
    with col_right:
        render_pipeline_status()

    # Infrastructure Control Plane (Metrics moved to bottom for space)
    st.divider()
    render_ai_engine_telemetry()
    render_ai_analyst()
    render_incident_ledger()

    # Heartbeat: Tick every second if breach simulation is active
    if breach_sim:
        time.sleep(1)
        st.rerun()


if __name__ == "__main__":
    main()
