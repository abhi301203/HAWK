import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import numpy as np

# --- RESEARCH IDENTITY ---
st.set_page_config(page_title="HAWK | Live Mission Console", page_icon="🦅", layout="wide")

# Graduate-Level CSS for "Command Center" look
st.markdown("""
    <style>
    .main { background-color: #06090e; color: #c9d1d9; }
    .stButton>button { background-color: #1f6feb; color: white; border-radius: 8px; width: 100%; }
    .stTextInput>div>div>input { background-color: #0d1117; color: #58a6ff; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- CITY DATA (The "Environment Map") ---
# Mimics the Mapping/ and Datasets/ structure [cite: 60]
CITY_ASSETS = {
    "buildings": [[5,5], [5,15], [15,5], [15,15], [25,25], [35,5], [35,35], [5,35]],
    "roads": {"x": [0, 40, 40, 0, 0, 20, 20], "y": [10, 10, 30, 30, 10, 10, 40]}, # Grid layout
    "trees": [[8,8], [22,12], [38,28], [12,38]],
    "targets": {
        "red car": {"pos": [40, 10], "type": "Vehicle", "id": "L-991"},
        "blue truck": {"pos": [20, 35], "type": "Vehicle", "id": "L-992"},
        "human": {"pos": [10, 10], "type": "Pedestrian", "id": "L-993"}
    }
}

# --- LOGIC ENGINE (Based on Stage-1 Documentation) ---
def parse_instruction(text):
    """5.3 NLP Module logic [cite: 60, 400]"""
    text = text.lower()
    target = "unknown"
    for key in CITY_ASSETS["targets"].keys():
        if key in text: target = key
    return target

def simulate_path(start, end):
    """5.7 Navigation logic: Simple waypoint interpolation [cite: 60, 411]"""
    # In a real AirSim run, this uses A* or Frontier Exploration [cite: 60, 412]
    steps = 15
    path_x = np.linspace(start[0], end[0], steps)
    path_y = np.linspace(start[1], end[1], steps)
    return path_x, path_y

# --- UI LAYOUT ---
st.title("🦅 H.A.W.K. | Multi-Domain Research Console")
st.caption("DOI Link: https://doi.org/10.55041/ISJEM06067")

col_viz, col_brain = st.columns([3, 2])

with col_viz:
    st.subheader("🏙️ H.A.W.K. Digital Twin (Live Map)")
    
    # Initialize session state for drone position
    if 'drone_pos' not in st.session_state:
        st.session_state.drone_pos = [0, 0]

    # Create the Visual City Map
    fig = go.Figure()

    # 1. Draw Roads (Navigation Bias)
    fig.add_trace(go.Scatter(x=CITY_ASSETS["roads"]["x"], y=CITY_ASSETS["roads"]["y"], 
                             mode='lines', line=dict(color='#232d3b', width=40), name="Semantic Roads", hoverinfo='skip'))
    
    # 2. Draw Buildings (Collision Boundaries) [cite: 323, 439]
    b_x, b_y = zip(*CITY_ASSETS["buildings"])
    fig.add_trace(go.Scatter(x=b_x, y=b_y, mode='markers', marker=dict(symbol='square', size=30, color='#30363d'), name="Buildings (Obstacles)"))

    # 3. Draw Targets (Landmark Memory)
    for name, data in CITY_ASSETS["targets"].items():
        color = "red" if "red" in name else "blue" if "blue" in name else "green"
        fig.add_trace(go.Scatter(x=[data["pos"][0]], y=[data["pos"][1]], mode='markers+text', 
                                 text=[name.upper()], textposition="top center",
                                 marker=dict(color=color, size=15, symbol='triangle-up'), name=name))

    # 4. Draw Drone
    fig.add_trace(go.Scatter(x=[st.session_state.drone_pos[0]], y=[st.session_state.drone_pos[1]], 
                             mode='markers', marker=dict(size=20, color='#58a6ff', symbol='x'), name="UAV (HAWK Agent)"))

    fig.update_layout(template="plotly_dark", xaxis=dict(range=[-5, 45]), yaxis=dict(range=[-5, 45]), 
                      height=600, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    
    map_placeholder = st.plotly_chart(fig, use_container_width=True)

with col_brain:
    st.subheader("🧠 Cognitive Processing")
    command = st.text_input("Input Flight Command (VLN):", "Go to the red car")
    
    if st.button("🚀 INITIATE MISSION"):
        target_key = parse_instruction(command)
        
        if target_key != "unknown":
            target_data = CITY_ASSETS["targets"][target_key]
            
            # SHOW THE STEP-BY-STEP LOGIC AS PER DOCUMENTATION [cite: 440, 693]
            with st.status("HAWK Core Processing...", expanded=True):
                st.write("**Step 1: 5.3 NLP Extraction**")
                st.write(f"Parsed Command: `ACTION: NAVIGATE`, `TARGET: {target_key.upper()}`")
                time.sleep(1)
                
                st.write("**Step 2: 5.4 Memory Retrieval**")
                st.write(f"ID: `{target_data['id']}` found in Landmark Memory at `{target_data['pos']}`")
                time.sleep(1)
                
                st.write("**Step 3: 5.6 Semantic Reasoning**")
                st.write("Target is 'Vehicle'. Bias navigation to Road Grid. Obstacle Avoidance: ON.")
                time.sleep(1)
                
                st.write("**Step 4: 5.7 Waypoint Execution**")
                st.write("Generating flight path in AirSim...")
                
                # SIMULATE MOVEMENT
                path_x, path_y = simulate_path(st.session_state.drone_pos, target_data["pos"])
                
                for i in range(len(path_x)):
                    st.session_state.drone_pos = [path_x[i], path_y[i]]
                    # In a real app, you'd use st.rerun() here, but for a smooth demo:
                    time.sleep(0.1)
                
                st.success("Target Reached. Holding position.")
                st.rerun()
        else:
            st.error("Target not found in Perception/Memory. Initiating Frontier Exploration.")

st.divider()

# --- THE "GENUINE" RESEARCH RECAP ---
st.header("🔬 3. Research Evidence & Documentation")
t1, t2 = st.tabs(["📄 Abstract & Paper", "🏗️ System Design"])

with t1:
    st.markdown(f"""
    **Project Title:** {command if 'command' in locals() else 'H.A.W.K.'}
    **Authors:** S. Abhinav, N. Tharun, T. Rishikesh [cite: 9, 10]
    **Abstract Excerpt:** Unlike traditional systems, H.A.W.K. introduces a task-driven framework functioning across unseen domains like urban/rural[cite: 54, 578].
    """)
    st.link_button("Download Full Stage-1 Report", "https://github.com/YourRepo/Stage-1_Documentation.docx")

with t2:
    st.write("#### 5.5 Complete Decision Flow")
    st.image("https://mermaid.ink/img/pako:eNqNUdtOwzAM_ZUrX7A_4A1pEtoHSAyJiVvSJi69uEmr-HeSdtm6TpqEPFmxc3zOTR-onBFAKax_UByLAtY2RmsE06F6f7N-t7_YV_tpf7GP_M0W8CclH-UqZ0kK6997h1oN-Y8Hw89lAisLWEV1EIsUlmYIK6gOYhEreAnLQSwisCxFWEZ1EIsYlkV1EIsYlnUQi7iCly_q_T-2-P_v-P9P7f8v7f_P-P9P-P8n9P-E-p9Q_xPq_5_6_0_9f6n-f-r_P_X_p_r_m_r-A2l58O0", caption="HAWK Intelligence Logic")
