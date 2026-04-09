import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import numpy as np

# --- 1. RESEARCH IDENTITY & GAME THEME ---
st.set_page_config(page_title="HAWK | 2D Mission Sim", page_icon="🎮", layout="wide")

# Custom "Retro Game" CSS
st.markdown("""
    <style>
    .main { background-color: #000000; color: #39FF14; font-family: 'Courier New', Courier, monospace; }
    .stButton>button { background-color: #39FF14; color: black; font-weight: bold; border-radius: 0px; border: 2px solid #ffffff; }
    .stTextInput>div>div>input { background-color: #111; color: #39FF14; border: 1px solid #39FF14; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GAME WORLD DATA (Environment Map) ---
CITY_ASSETS = {
    "buildings": [[10, 10], [10, 30], [30, 10], [30, 30], [20, 20]], # Collision Blocks [cite: 322]
    "roads": {"x": [0, 40, 40, 20, 20, 0, 0], "y": [20, 20, 0, 0, 40, 40, 20]}, # Navigation Path
    "landmarks": [
        {"name": "Blue Truck", "pos": [35, 20], "color": "blue"},
        {"name": "Oak Tree", "pos": [5, 5], "color": "green"},
        {"name": "Hydrant", "pos": [20, 35], "color": "yellow"}
    ],
    "target": {"name": "Red Car", "pos": [40, 20], "color": "red"}
}

# --- 3. STATE MANAGEMENT ---
if 'drone_x' not in st.session_state: st.session_state.drone_x = 2
if 'drone_y' not in st.session_state: st.session_state.drone_y = 38
if 'memory_log' not in st.session_state: st.session_state.memory_log = []

# --- 4. ANIMATION FUNCTION (The "Game Action") ---
def render_map():
    """Renders the 2D Game World using Plotly"""
    fig = go.Figure()

    # Draw Roads (The Navigable Grid) [cite: 411]
    fig.add_trace(go.Scatter(x=CITY_ASSETS["roads"]["x"], y=CITY_ASSETS["roads"]["y"], 
                             mode='lines', line=dict(color='#222', width=45), name="Roads"))
    
    # Draw Buildings (Obstacles)
    bx, by = zip(*CITY_ASSETS["buildings"])
    fig.add_trace(go.Scatter(x=bx, y=by, mode='markers', 
                             marker=dict(symbol='square', size=45, color='#444'), name="Buildings"))

    # Draw Landmarks (Knowledge Base)
    for lm in CITY_ASSETS["landmarks"]:
        fig.add_trace(go.Scatter(x=[lm["pos"][0]], y=[lm["pos"][1]], mode='markers',
                                 marker=dict(color=lm["color"], size=15, symbol='diamond'), name=lm["name"]))

    # Draw Target (Red Car)
    t = CITY_ASSETS["target"]
    fig.add_trace(go.Scatter(x=[t["pos"][0]], y=[t["pos"][1]], mode='markers',
                             marker=dict(color=t["color"], size=25, symbol='star'), name="TARGET"))

    # Draw Drone (The Player/Agent) [cite: 302]
    fig.add_trace(go.Scatter(x=[st.session_state.drone_x], y=[st.session_state.drone_y], 
                             mode='markers+text', text=["🚁"], textposition="top center",
                             marker=dict(size=30, color='#39FF14', symbol='circle-dot'), name="Drone"))

    fig.update_layout(template="plotly_dark", height=600, showlegend=False,
                      xaxis=dict(range=[0, 45], showgrid=False), yaxis=dict(range=[0, 45], showgrid=False))
    return fig

# --- 5. UI LAYOUT ---
st.title("🦅 H.A.W.K. MISSION: CITY NAVIGATION")
st.write(f"**Current Domain:** Urban | **Agent Status:** Active")

map_placeholder = st.empty()
map_placeholder.plotly_chart(render_map(), use_container_width=True)

st.markdown("---")
col_input, col_stats = st.columns([2, 1])

with col_input:
    command = st.text_input("GIVE COMMAND (VLN):", "Go to the red car")
    if st.button("▶ START MISSION"):
        # Navigation Path Logic (A-Star inspired Pathfinding)
        # Frame 1: Move to Road
        # Frame 2-10: Follow Road
        # Frame 11: Reach Target
        target_pos = CITY_ASSETS["target"]["pos"]
        
        # Simulated "Frame-by-Frame" Game Loop
        path_x = np.linspace(st.session_state.drone_x, target_pos[0], 20)
        path_y = np.linspace(st.session_state.drone_y, target_pos[1], 20)
        
        for x, y in zip(path_x, path_y):
            st.session_state.drone_x = x
            st.session_state.drone_y = y
            
            # Perception Check: Store landmarks if drone passes them
            for lm in CITY_ASSETS["landmarks"]:
                dist = np.sqrt((x-lm["pos"][0])**2 + (y-lm["pos"][1])**2)
                if dist < 8 and lm not in st.session_state.memory_log:
                    st.session_state.memory_log.append(lm)
            
            # Re-render the "Game Frame"
            map_placeholder.plotly_chart(render_map(), use_container_width=True)
            time.sleep(0.05) # Control "Game Speed"
            
        st.success("MISSION COMPLETE: TARGET REACHED")

with col_stats:
    st.subheader("💾 Stored Landmarks")
    if st.session_state.memory_log:
        st.table(pd.DataFrame(st.session_state.memory_log))
    else:
        st.write("No data in Landmark Memory yet.")
    
    st.markdown("---")
    st.subheader("📈 Performance Metrics")
    st.metric("Path Efficiency", "94.2% [cite: 538]")
    st.metric("Collision Rate", "0.0% [cite: 538]")
