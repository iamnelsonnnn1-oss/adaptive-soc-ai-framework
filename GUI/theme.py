import streamlit as st

def inject_cockpit_css():
    """Injects aviation-grade ergonomics and visual hierarchy."""
    st.markdown("""
        <style>
        /* Glass Cockpit Matte Foundation */
        .stApp {
            background-color: #050505 !important;
            color: #E0E0E0 !important;
            font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif !important;
        }
        
        /* Panel Framing */
        [data-testid="column"] {
            background: rgba(15, 15, 15, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 15px !important;
            border-radius: 2px;
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
            font-family: 'Courier New', monospace;
            font-size: 1.8rem;
            color: #00FF00; /* Phosphor Green */
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
            background-color: #1A1A1A !important;
            color: #FFFFFF !important;
            border: 1px solid #333333 !important;
            border-radius: 0px !important;
            font-size: 0.7rem !important;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.2s;
            width: 100%;
        }
        div.stButton > button:hover {
            border-color: #00FF00 !important;
            color: #00FF00 !important;
            background-color: #0A1A0A !important;
        }

        /* Flight Status Bar (Header) */
        .flight-status-bar {
            background: #000000;
            border-bottom: 2px solid #333333;
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
            background-color: #00FF00;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        </style>
    """, unsafe_allow_html=True)