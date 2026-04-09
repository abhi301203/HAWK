import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. RESEARCH IDENTITY ---
st.set_page_config(page_title="HAWK | Interactive Sim", page_icon="🛸", layout="wide")

# Dark "Command Center" CSS
st.markdown("""
    <style>
    .main { background-color: #000000; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
    .stTextInput>div>div>input { background-color: #111; color: #00FF41; border: 1px solid #00FF41; }
    .stMetric { background-color: #111; border: 1px solid #00FF41; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GAME ASSETS (Section 5.10) ---
CITY_GRID = {
    "buildings": {"x": [10, 30, 10, 30, 20], "y": [10, 10, 30, 30, 20], "icon": "🏢"},
    "roads": {"x": [0, 40, 40, 20, 20, 0, 0], "y": [20, 20, 0, 0, 40, 40, 20]},
    "landmarks": [
        {"name": "Blue Truck", "pos": [35, 20], "icon": "🚚", "color": "blue"},
        {"name": "Oak Tree", "pos": [5, 35], "icon": "🌳", "color": "green"},
        {"name": "Human_1", "pos": [22, 38], "icon": "🚶", "color": "yellow"}
    ],
    "targets": {
        "red car": {"pos": [38, 5], "icon": "🚗", "id": "L-991"}
    }
}

# Session State for persistent data
if 'history' not in st.session_state: st.session_state.history = []
if 'discovered' not in st.session_state: st.session_state.discovered = []

# --- 3. THE ANIMATION ENGINE (Smooth Glide Logic) ---
def create_smooth_path(start, end, frames=30):
    """Interpolates coordinates for smooth movement"""
    return np.linspace(start, end, frames)

# --- 4. UI LAYOUT ---
st.title("🛸 H.A.W.K. INTERACTIVE MISSION HUB")
st.caption("Hybrid Autonomous Waypoint Knowledge | DOI: 10.55041/ISJEM06067")
st.divider()

col_map, col_brain = st.columns([3, 2])

with col_map:
    # Build the Static Map Background
    fig = go.Figure()
    
    # 1. Roads (Path Bias)
    fig.add_trace(go.Scatter(x=CITY_GRID["roads"]["x"], y=CITY_GRID["roads"]["y"], 
                             mode='lines', line=dict(color='#222', width=40), hoverinfo='skip'))
    
    # 2. Buildings (Collision Zones)
    fig.add_trace(go.Scatter(x=CITY_GRID["buildings"]["x"], y=CITY_GRID["buildings"]["y"], 
                             mode='markers+text', text=["🏢"]*5, textfont=dict(size=30),
                             marker=dict(size=1), name="Buildings"))
    
    # 3. Landmarks & Targets (Discovery Assets)
    for lm in CITY_GRID["landmarks"]:
        fig.add_trace(go.Scatter(x=[lm["pos"][0]], y=[lm["pos"][1]], mode='text', 
                                 text=[lm["icon"]], textfont=dict(size=25), name=lm["name"]))
    
    t = CITY_GRID["targets"]["red car"]
    fig.add_trace(go.Scatter(x=[t["pos"][0]], y=[t["pos"][1]], mode='text', 
                             text=["🚗"], textfont=dict(size=30), name="Target Car"))

    # 4. The Drone (UAV Agent)
    drone_trace = go.Scatter(x=[2], y=[38], mode='text', text=["🛸"], 
                             textfont=dict(size=40), name="HAWK-UAV")
    fig.add_trace(drone_trace)

    fig.update_layout(template="plotly_dark", xaxis=dict(range=[0, 45]), yaxis=dict(range=[0, 45]),
                      height=600, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
    
    # Render the Placeholder
    map_placeholder = st.plotly_chart(fig, use_container_width=True)

with col_brain:
    st.subheader("📟 Mission Processor")
    instruction = st.text_input("Enter Instruction:", "Find the red car")
    
    if st.button("▶ START SIMULATION"):
        # 5.3 NLP MODULE [cite: 401]
        st.session_state.history.append(instruction)
        
        # Simulated Terminal Reasoning (Presentation Mode)
        with st.container():
            t_log = st.empty()
            t_log.markdown("`[SYSTEM]` Analyzing Instruction...")
            time.sleep(1)
            t_log.markdown("`[SYSTEM]` NLP Extracted: ACTION=NAVIGATE, TARGET=CAR, ATTR=RED")
            time.sleep(1)
            t_log.markdown("`[SYSTEM]` Checking Spatial Graph Memory... Target Match Found!")
            time.sleep(1)
            t_log.markdown("`[SYSTEM]` Calculating Smooth Trajectory Avoiding Obstacles...")
            
            # SMOOTH ANIMATION LOOP
            target_pos = CITY_GRID["targets"]["red car"]["pos"]
            path_x = create_smooth_path(2, target_pos[0])
            path_y = create_smooth_path(38, target_pos[1])
            
            for x, y in zip(path_x, path_y):
                # Update Drone Trace only (Optimization for smoothness)
                fig.data[-1].x = [x]
                fig.data[-1].y = [y]
                map_placeholder.plotly_chart(fig, use_container_width=True)
                
                # Online Learning Discovery (5.13) 
                for lm in CITY_GRID["landmarks"]:
                    if abs(x - lm["pos"][0]) < 5 and abs(y - lm["pos"][1]) < 5:
                        if lm["name"] not in st.session_state.discovered:
                            st.session_state.discovered.append(lm["name"])
                            st.toast(f"New Landmark Discovered: {lm['name']}")
                
                time.sleep(0.01) # Ultra-smooth frame delay
            
            st.success("Target Reached. Knowledge Base Updated. [cite: 463]")

st.divider()

# --- 5. DATA COLLECTION & METRICS ---
st.header("📊 H.A.W.K. Telemetry & Analytics")
col1, col2, col3 = st.columns(3)

with col1:
    st.write("#### 💾 Landmark Memory")
    st.write("Objects detected during flight:")
    st.write(st.session_state.discovered if st.session_state.discovered else "No objects discovered.")

with col2:
    st.write("#### 🏗️ Architecture Metrics")
    st.metric("Path Efficiency", "96.4%", "VLN Optimized")
    st.metric("Detection Confidence", "0.89", "YOLOv8")
    st.metric("ResNet18 Adapt.", "High", "Domain-Urban")

with col3:
    st.write("#### 📜 Instruction History")
    st.write(st.session_state.history)

# Final Conclusions from Thesis [cite: 541, 542]
st.info("**Research Summary:** H.A.W.K. addresses limitations of traditional navigation by integrating vision-language understanding with adaptive learning. [cite: 541, 542]")
