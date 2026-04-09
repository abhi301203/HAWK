import streamlit as st

def apply_custom_style():
    st.markdown("""
        <style>
        /* Modern Google-esque Typography */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;500&family=Space+Mono&display=swap');
        
        /* Responsive Container */
        .block-container { padding: 1rem 2rem !important; max-width: 1200px !important; }
        
        /* Professional Dark Mode HUD */
        .main { background-color: #080808; color: #e0e0e0; font-family: 'Roboto', sans-serif; }
        
        /* Unified Component Styling */
        .stMetric { background: #121212; border: 1px solid #333; border-radius: 8px; padding: 10px; }
        .terminal-text { font-family: 'Space Mono', monospace; color: #00FF41; font-size: 0.85rem; }
        
        /* Compact Map for Mobile/Windows */
        .plotly-graph-div { border-radius: 12px; border: 1px solid #444; }
        
        /* High-Visibility Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #00FF41 0%, #008f25 100%);
            color: black; font-weight: 700; border: none; width: 100%; border-radius: 6px;
        }
        </style>
    """, unsafe_allow_html=True)
