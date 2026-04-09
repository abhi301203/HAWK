import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=JetBrains+Mono:wght@300;500&display=swap');
        
        .main { background: #000000; color: #00FF41; font-family: 'JetBrains Mono', monospace; }
        .stApp { background: linear-gradient(180deg, #050505 0%, #000000 100%); }
        
        /* Tactical HUD Header */
        .hud-header {
            border-left: 5px solid #00FF41;
            padding-left: 15px;
            margin-bottom: 25px;
            background: rgba(0, 255, 65, 0.05);
        }
        
        /* Terminal Styling */
        .terminal-box {
            background: #0a0a0a;
            border: 1px solid #1a1a1a;
            border-radius: 5px;
            padding: 15px;
            box-shadow: inset 0 0 10px #000;
        }
        
        /* Metric Cards */
        [data-testid="stMetricValue"] { font-family: 'Orbitron', sans-serif; color: #00FF41 !important; text-shadow: 0 0 10px #00FF41; }
        
        /* Progress Bar */
        .stProgress > div > div > div > div { background-color: #00FF41; }
        
        /* Buttons */
        .stButton>button {
            width: 100%;
            background: transparent;
            color: #00FF41;
            border: 1px solid #00FF41;
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 2px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00FF41;
            color: black;
            box-shadow: 0 0 20px #00FF41;
        }
        </style>
    """, unsafe_allow_html=True)
