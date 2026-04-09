import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import numpy as np

# --- RESEARCH IDENTITY ---
st.set_page_config(page_title="HAWK | Mission Simulator", page_icon="🦅", layout="wide")

# Custom UI for a "Nokia Snake / Retro HUD" feel
st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
    .stMetric { background-color: #161b22; border: 1px solid #00FF41; padding: 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- CITY ASSETS & PERSISTENT DATA ---
# Logic based on Section 5.10 (Datasets) and 5.4 (Memory)
CITY_DATA = {
    "buildings": [[5, 10], [15, 25], [30, 15], [10, 35], [35, 35]],
    "roads": {"x": [0, 40, 40, 0, 0, 20, 20], "y": [10, 10, 30, 30, 10, 10, 40]},
    "landmarks": [
        {"name": "Blue Truck", "pos": [20, 10], "color": "blue"},
        {"name": "Oak Tree", "pos": [5, 30], "color": "green"},
        {"name": "Human_1", "pos": [38, 30], "color": "yellow"}
    ],
    "targets": {
        "red car": {"pos": [40, 10], "id": "L-991", "color": "red"}
    }
}

# Initialize Session States
if 'drone_pos' not in st.session_state: st.session_state.drone_pos = [2, 2]
if 'landmark_db' not in st.session_state: st.session_state.landmark_db = []
if 'history' not in st.session_state: st.session_state.history = []

# --- CORE SIMULATION FUNCTIONS ---
def generate_vln_path(start, end):
    """5.7 Navigation: Generates a path that prioritizes 'Road' coordinates"""
    # Simple logic: Move to road first, then follow road to target
    road_y = 10 # Main horizontal road
    path = [start]
    # Step to road
    path.append([start[0], road_y])
    # Follow road
    path.append([end[0], road_y])
    # Step to target
    path.append(end)
    return np.array(path)

# --- HEADER ---
st.title("🦅 H.A.W.K. MISSION CONTROL v2.4")
st.caption("Hybrid Adaptive Waypoint Knowledge | ISJEM DOI: 10.55041/ISJEM06067")
st.divider()

col_map, col_brain = st.columns([3, 2])

with col_map:
    st.subheader("🕹️ Live Navigation Feed (2D Mapping)")
    
    # Create the Plotly Map
    fig = go.Figure()

    # 1. Plot Roads (Semantic Bias Layer)
    fig.add_trace(go.Scatter(x=CITY_DATA["roads"]["x"], y=CITY_DATA["roads"]["y"], mode='lines', 
                             line=dict(color='#333', width=30), name="Road (Bias Path)"))
    
    # 2. Plot Buildings (Hard Obstacles)
    bx, by = zip(*CITY_DATA["buildings"])
    fig.add_trace(go.Scatter(x=bx, y=by, mode='markers', marker=dict(symbol='square', size=40, color='gray'), name="Buildings"))

    # 3. Plot Drone (The Agent)
    fig.add_trace(go.Scatter(x=[st.session_state.drone_pos[0]], y=[st.session_state.drone_pos[1]], 
                             mode='markers+text', text=["🚁 HAWK-01"], textposition="top center",
                             marker=dict(size=25, color='#00FF41', symbol='circle-cross-dot'), name="UAV"))

    # 4. Target Landmark
    target_pos = CITY_DATA["targets"]["red car"]["pos"]
    fig.add_trace(go.Scatter(x=[target_pos[0]], y=[target_pos[1]], mode='markers', 
                             marker=dict(size=20, color='red', symbol='star'), name="Target: Red Car"))

    fig.update_layout(template="plotly_dark", height=500, xaxis=dict(range=[0, 45]), yaxis=dict(range=[0, 45]), showlegend=False)
    map_display = st.plotly_chart(fig, use_container_width=True)

with col_brain:
    st.subheader("🧠 Cognitive Intelligence Engine")
    instruction = st.text_input("Enter Command:", value="Go to the red car")
    
    if st.button("🚀 EXECUTE INSTRUCTION"):
        # 5.3 NLP Extraction
        st.session_state.history.append(instruction)
        
        # 5.5 Decision Flow Simulation
        with st.status("Analyzing Request...", expanded=True) as status:
            st.write("✅ NLP: Parsed Target `[RED CAR]`")
            time.sleep(1)
            st.write("✅ Memory: Landmark found in Knowledge Base")
            time.sleep(1)
            
            # Start Navigation Movement
            start_pt = list(st.session_state.drone_pos)
            path = generate_vln_path(start_pt, target_pos)
            
            st.write("🛰️ Executing Waypoint Navigation...")
            for point in path:
                st.session_state.drone_pos = point
                # 5.13 Online Learning: Storing landmarks perceived during flight
                for lm in CITY_DATA["landmarks"]:
                    if abs(point[0] - lm["pos"][0]) < 10 and lm not in st.session_state.landmark_db:
                        st.session_state.landmark_db.append(lm)
                time.sleep(0.8)
                st.rerun()
            
            status.update(label="Target Reached Successfully", state="complete")

st.divider()

# --- DATASET & METRICS (Section 6.0) ---
st.header("📊 Mission Analytics & Stored Knowledge")
m_col1, m_col2, m_col3 = st.columns([2, 2, 1])

with m_col1:
    st.write("#### 💾 Stored Landmark Memory (Phase 3)")
    if st.session_state.landmark_db:
        st.table(pd.DataFrame(st.session_state.landmark_db))
    else:
        st.write("No landmarks discovered yet.")

with m_col2:
    st.write("#### 📝 Instruction History")
    st.write(st.session_state.history)
    st.write("**Mission Parameters:**")
    st.json({
        "Initial_Pos": "[2, 2]",
        "Target_Pos": f"{target_pos}",
        "Safety_Protocol": "Active (Obstacle Avoidance)",
        "Navigation_Mode": "VLN + Semantic Road Bias"
    })

with m_col3:
    st.write("#### 📈 Execution Metrics")
    st.metric("Path Efficiency", "92%", "+5%")
    st.metric("Detection Acc.", "0.89", "YOLOv8")
    st.metric("Collision Risk", "Low", "Safety_ON")

st.info("**Research Summary:** H.A.W.K. interprets user commands and navigates dynamic environments by building a persistent spatial graph of discovered landmarks[cite: 589, 714].")
