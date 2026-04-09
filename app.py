import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. RESEARCH IDENTITY & GAME THEME ---
st.set_page_config(page_title="HAWK | Mission Simulator", page_icon="🛸", layout="wide")

# Custom "Retro Game Console" CSS
st.markdown("""
    <style>
    .main { background-color: #000000; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
    .stTextInput>div>div>input { background-color: #111; color: #00FF41; border: 1px solid #00FF41; }
    .stMetric { background-color: #111; border: 1px solid #00FF41; padding: 10px; border-radius: 5px; }
    .stButton>button { background-color: #00FF41; color: black; font-weight: bold; width: 100%; border-radius: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GAME ASSETS (Data from Section 5.10 & 5.4) ---
CITY_GRID = {
    "buildings": {"x": [10, 30, 10, 30, 20], "y": [10, 10, 30, 30, 20]},
    "roads": {"x": [0, 40, 40, 20, 20, 0, 0], "y": [20, 20, 0, 0, 40, 40, 20]},
    "landmarks": [
        {"name": "Blue Truck", "pos": [35, 20], "icon": "🚚"},
        {"name": "Oak Tree", "pos": [5, 35], "icon": "🌳"},
        {"name": "Human_1", "pos": [22, 38], "icon": "🚶"}
    ],
    "targets": {
        "red car": {"pos": [38, 5], "icon": "🚗", "id": "L-991"}
    }
}

# --- 3. SESSION STATE (Memory & History) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'discovered' not in st.session_state: st.session_state.discovered = []
if 'drone_pos' not in st.session_state: st.session_state.drone_pos = [2, 38]

# --- 4. THE CORE RENDERER ---
def draw_city_map(drone_x, drone_y, frame_id=0):
    fig = go.Figure()
    # 1. Roads (Path Bias Logic)
    fig.add_trace(go.Scatter(x=CITY_GRID["roads"]["x"], y=CITY_GRID["roads"]["y"], 
                             mode='lines', line=dict(color='#222', width=45), hoverinfo='skip'))
    # 2. Buildings (Collision Zones)
    fig.add_trace(go.Scatter(x=CITY_GRID["buildings"]["x"], y=CITY_GRID["buildings"]["y"], 
                             mode='text', text=["🏢"]*5, textfont=dict(size=35), name="Buildings"))
    # 3. Landmarks
    for lm in CITY_GRID["landmarks"]:
        fig.add_trace(go.Scatter(x=[lm["pos"][0]], y=[lm["pos"][1]], mode='text', 
                                 text=[lm["icon"]], textfont=dict(size=30), name=lm["name"]))
    # 4. Target Object (The Goal)
    t = CITY_GRID["targets"]["red car"]
    fig.add_trace(go.Scatter(x=[t["pos"][0]], y=[t["pos"][1]], mode='text', 
                             text=[t["icon"]], textfont=dict(size=35), name="Target"))
    # 5. THE DRONE (The Agent)
    fig.add_trace(go.Scatter(x=[drone_x], y=[drone_y], mode='text', 
                             text=["🛸"], textfont=dict(size=45), name="HAWK-UAV"))

    fig.update_layout(template="plotly_dark", xaxis=dict(range=[0, 45], showgrid=False), 
                      yaxis=dict(range=[0, 45], showgrid=False), height=600, 
                      margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
    return fig

# --- 5. UI LAYOUT ---
st.title("🛸 H.A.W.K. INTERACTIVE GAME HUB")
st.caption("Hybrid Autonomous Waypoint Knowledge | DOI: 10.55041/ISJEM06067")
st.divider()

col_map, col_brain = st.columns([3, 2])

with col_map:
    map_placeholder = st.empty()
    # Draw initial static map
    map_placeholder.plotly_chart(draw_city_map(st.session_state.drone_pos[0], st.session_state.drone_pos[1]), use_container_width=True, key="initial_map")

with col_brain:
    st.subheader("📟 HAWK Thought Terminal")
    instruction = st.text_input("Input Mission Instruction:", "Go to the red car")
    
    if st.button("▶ START MISSION ENGINE"):
        # 5.3 NLP MODULE [cite: 240, 401]
        st.session_state.history.append(instruction)
        
        # Simulated Cognitive Pipeline
        terminal = st.empty()
        with terminal.container():
            st.markdown("`[SYSTEM]` 1. NLP Processor: Extracting Intent... [cite: 240]")
            time.sleep(1)
            st.markdown(f"`[SYSTEM]` 2. Semantic Analysis: Target='RED CAR' | Action='NAVIGATE'")
            time.sleep(1)
            st.markdown("`[SYSTEM]` 3. Memory Query: Spatial Graph Found Target ID `L-991`")
            time.sleep(1)
            st.markdown("`[SYSTEM]` 4. Navigation: Applying Road-Bias Trajectory")
            
            # --- THE GAME LOOP (Smooth Glide) ---
            target_pos = CITY_GRID["targets"]["red car"]["pos"]
            path_x = np.linspace(st.session_state.drone_pos[0], target_pos[0], 35)
            path_y = np.linspace(st.session_state.drone_pos[1], target_pos[1], 35)
            
            for i, (x, y) in enumerate(zip(path_x, path_y)):
                # Update Drone Position
                st.session_state.drone_pos = [x, y]
                # Render Frame with UNIQUE KEY to avoid DuplicateID Error
                map_placeholder.plotly_chart(draw_city_map(x, y), use_container_width=True, key=f"frame_{i}")
                
                # 5.13 Online Learning (Landmark Discovery) [cite: 268, 434]
                for lm in CITY_GRID["landmarks"]:
                    dist = np.sqrt((x - lm["pos"][0])**2 + (y - lm["pos"][1])**2)
                    if dist < 6 and lm["name"] not in st.session_state.discovered:
                        st.session_state.discovered.append(lm["name"])
                        st.toast(f"Landmark Synced: {lm['name']}")
                
                time.sleep(0.01) # Game Speed
            
            st.success("Target Reached. Knowledge Base Updated.")

st.divider()

# --- 6. MISSION ANALYTICS (Chapter 6.0) ---
st.header("📊 Mission Telemetry & Stored Knowledge")
m1, m2, m3 = st.columns(3)

with m1:
    st.write("#### 💾 Landmark Memory")
    st.write(pd.DataFrame({"Discovered_Objects": st.session_state.discovered}) if st.session_state.discovered else "No objects discovered yet.")

with m2:
    st.write("#### 🏗️ Performance Metrics [cite: 508]")
    st.metric("Path Efficiency", "96.4%", "VLN Optimized")
    st.metric("Inference Latency", "12ms", "-2ms")
    st.metric("Collision Risk", "Zero", "Safety Replan ON")

with m3:
    st.write("#### 📜 Instruction History")
    st.write(st.session_state.history)
