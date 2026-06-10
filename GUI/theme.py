import streamlit as st

def inject_cockpit_css():
    """Injects aviation-grade ergonomics and visual hierarchy."""
    st.markdown("""
        <style>
        /* Darktrace-Inspired NDR Foundation */
        .stApp {
            background-color: #00080B !important;
            background-image: radial-gradient(circle at 50% 50%, #001A1F 0%, #00080B 100%) !important;
            color: #D1F7FF !important;
            font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif !important;
        }
        
        /* Panel Framing */
        [data-testid="column"] {
            background: rgba(0, 12, 15, 0.7) !important;
            border: 1px solid rgba(0, 245, 255, 0.08) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 20px !important;
            border-radius: 4px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        [data-testid="column"]:hover {
            border: 1px solid rgba(0, 245, 255, 0.3) !important;
            box-shadow: 0 0 20px rgba(0, 245, 255, 0.1);
        }

        /* Instrumentation Typography */
        .metric-label {
            font-size: 0.65rem;
            color: #777777;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.8rem;
            color: #00F5FF; /* Cyber Cyan */
            text-shadow: 0 0 10px rgba(0, 245, 255, 0.3);
        }

        /* Master Caution Logic */
        @keyframes master-pulse {
            0% { border-color: #FF0000; box-shadow: 0 0 5px #FF0000; }
            50% { border-color: #FF0000; box-shadow: 0 0 20px #FF0000; }
            100% { border-color: #FF0000; box-shadow: 0 0 5px #FF0000; }
        }
        .alert-master {
            border: 2px solid #FF0000 !important;
            animation: master-pulse 1s infinite;
        }

        /* Cockpit Switchgear (Buttons) */
        div.stButton > button {
            background-color: rgba(0, 245, 255, 0.03) !important;
            color: #00F5FF !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: 2px !important;
            font-size: 0.7rem !important;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.2s;
            width: 100%;
        }
        div.stButton > button:hover {
            border-color: #00F5FF !important;
            background-color: rgba(0, 245, 255, 0.1) !important;
            box-shadow: 0 0 15px rgba(0, 245, 255, 0.2);
        }

        /* Flight Status Bar (Header) */
        .flight-status-bar {
            background: rgba(0, 8, 11, 0.95);
            border-bottom: 1px solid rgba(0, 245, 255, 0.2);
            padding: 10px 25px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        /* Radar Terminal styling */
        .radar-terminal {
            background: #080808;
            border: 1px solid #1A1A1A;
            height: 400px;
            overflow-y: auto;
            padding: 10px;
            font-family: 'Courier New', monospace;
        }
        
        /* Mission Timeline */
        .timeline-entry {
            border-left: 2px solid #333333;
            padding-left: 15px;
            margin-bottom: 10px;
            font-size: 0.75rem;
        }

        /* Ingestion Pulse */
        .ingestion-online {
            height: 8px;
            width: 8px;
            background-color: #00F5FF;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }

        /* Custom Scrollbar for Analyst Terminal */
        ::-webkit-scrollbar {
            width: 4px;
        }
        ::-webkit-scrollbar-track {
            background: #050505;
        }
        ::-webkit-scrollbar-thumb {
            background: #00F5FF;
            border-radius: 10px;
        }

        </style>
    """, unsafe_allow_html=True)