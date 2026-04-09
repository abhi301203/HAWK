import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import time

# --- 1. IDEA: COMMAND & CONTROL INTERFACE ---
st.set_page_config(page_title="HAWK | Tactical Hub", page_icon="🛸", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
    .stMetric { background-color: #111; border: 1px solid #00FF41; padding: 10px; border-radius: 5px; }
    .stButton>button { background-color: #00FF41; color: black; font-weight: bold; width: 100%; border-radius: 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. IDEA: DIGITAL TWIN SPATIAL MAP (Data Layer) ---
CITY_KNOWLEDGE = {
    "infrastructure": {
        "roads": {"x": [0, 45, 45, 22, 22, 0, 0, 45], "y": [22, 22, 0, 0, 45, 45, 22, 22]},
        "buildings": [
            {"name": "HOSPITAL", "pos": [5, 40], "icon": "🏥"},
            {"name": "SCHOOL", "pos": [35, 40], "icon": "🏫"},
            {"name": "HOME", "pos": [40, 5], "icon": "🏠"}
        ]
    },
    "entities": [
        {"name": "RED CAR", "pos": [25, 21], "icon": "🚗"},
        {"name": "HUMAN", "pos": [23, 30], "icon": "🚶"}
    ]
}

if 'drone_pos' not in st.session_state: st.session_state.drone_pos = [2, 43]
if 'landmark_memory' not in st.session_state: st.session_state.landmark_memory = []

def render_tactical_map(dx, dy, trail_x=None, trail_y=None):
    fig = go.Figure()
    # Draw Road Bias Paths [cite: 107]
    fig.add_trace(go.Scatter(x=CITY_KNOWLEDGE["infrastructure"]["roads"]["x"], y=CITY_KNOWLEDGE["infrastructure"]["roads"]["y"], mode='lines', line=dict(color='#222', width=40), hoverinfo='skip'))
    # Draw Buildings [cite: 101]
    for b in CITY_KNOWLEDGE["infrastructure"]["buildings"]:
        fig.add_trace(go.Scatter(x=[b["pos"][0]], y=[b["pos"][1]], mode='text', text=[b["icon"]], textfont=dict(size=35), name=b["name"]))
    # Draw Drone
    fig.add_trace(go.Scatter(x=[dx], y=[dy], mode='text', text=["<b>X</b>"], textfont=dict(size=40, color="white"), name="UAV-HAWK"))
    
    fig.update_layout(template="plotly_dark", xaxis=dict(range=[0, 48], showgrid=False), yaxis=dict(range=[0, 48], showgrid=False), height=600, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
    return fig

# --- UI LAYOUT ---
st.title("🛸 H.A.W.K. PHASE 1: TACTICAL FOUNDATION")
st.divider()

col_map, col_brain = st.columns([3, 2])

with col_map:
    map_placeholder = st.empty()
    map_placeholder.plotly_chart(render_city_map(st.session_state.drone_pos[0], st.session_state.drone_pos[1]), use_container_width=True)

with col_brain:
    st.subheader("📟 IDEA: COGNITIVE REASONING PIPELINE")
    instruction = st.text_input("INPUT VLN COMMAND:", placeholder="e.g. Go to hospital")
    
    if st.button("▶ LAUNCH MISSION"):
        # 2. IDEA: STOCHASTIC LATENCY ENGINE
        with st.status("🧠 Processing...", expanded=True) as status:
            st.write("`[LOG]` Parsing Natural Language (SpaCy)...")
            time.sleep(1.2) # Artificial Latency 
            st.write("`[LOG]` Checking Persistent Landmark Memory...")
            time.sleep(0.8)
            
            # Find Target
            target = next((l for l in CITY_KNOWLEDGE["infrastructure"]["buildings"] if l["name"].lower() in instruction.lower()), None)
            
            if target:
                # 3. IDEA: COGNITIVE STEP-THROUGH
                st.write(f"`[LOG]` Waypoint Identified at {target['pos']}. Calculating Trajectory...")
                
                path_x = np.linspace(st.session_state.drone_pos[0], target["pos"][0], 50)
                path_y = np.linspace(st.session_state.drone_pos[1], target["pos"][1], 50)
                
                for i in range(50):
                    st.session_state.drone_pos = [path_x[i], path_y[i]]
                    
                    # 5. IDEA: ONLINE LEARNING DATABASE SYNC [cite: 127]
                    for ent in CITY_KNOWLEDGE["entities"]:
                        dist = np.sqrt((path_x[i]-ent["pos"][0])**2 + (path_y[i]-ent["pos"][1])**2)
                        if dist < 6 and ent not in st.session_state.landmark_memory:
                            st.session_state.landmark_memory.append(ent)
                            st.toast(f"Landmark Synced: {ent['name']}")

                    map_placeholder.plotly_chart(render_city_map(path_x[i], path_y[i]), use_container_width=True, key=f"mission_step_{i}")
                    time.sleep(0.01)
                
                status.update(label="MISSION SUCCESS", state="complete")

st.divider()
st.write("#### 💾 Knowledge Base (Current Perception)")
st.table(pd.DataFrame(st.session_state.landmark_memory) if st.session_state.landmark_memory else "Awaiting perception data...")
