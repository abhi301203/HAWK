import streamlit as st
import time
import pandas as pd

# --- UI CONFIG ---
st.set_page_config(page_title="HAWK | UAV Intelligence", page_icon="🦅", layout="wide")

# Custom CSS for a "Dark Mode" Tech feel
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; border: 1px solid #464b5d; }
    .stButton>button:hover { border: 1px solid #ff4b4b; color: #ff4b4b; }
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.title("🦅")
with col_title:
    st.title("H.A.W.K. MISSION CONTROL")
    st.caption("Hybrid Autonomous Waypoint Knowledge | Multi-Domain Navigation System")

st.divider()

# --- SIDEBAR: SYSTEM METRICS ---
with st.sidebar:
    st.header("🛸 Drone Telemetry")
    st.status("WSL Environment: CONNECTED", state="complete")
    st.status("AirSim Link: VIRTUAL_ACTIVE", state="running")
    st.status("YOLOv8 Engine: LOADED", state="complete")
    
    st.divider()
    st.subheader("Memory Stats")
    st.progress(78, text="Landmark Memory Density")
    st.progress(42, text="Domain Adaptation Progress")
    
    if st.button("🚨 Emergency Land"):
        st.error("Emergency Protocol Initiated...")

# --- MAIN INTERFACE: 3 COLUMNS ---
top_left, top_right = st.columns([2, 1])

with top_left:
    st.subheader("📡 Live Perception & Command")
    command = st.text_input("Human-Language Command:", placeholder="e.g., Find the red car and hover nearby")
    
    if st.button("Execute Mission"):
        if command:
            with st.status("Processing Instruction...", expanded=True) as status:
                st.write("🔍 Parsing Natural Language (SpaCy)...")
                time.sleep(1)
                st.write("🧠 Querying Object Cluster Memory...")
                time.sleep(1)
                st.write("🗺️ Generating Adaptive Waypoints...")
                time.sleep(1)
                status.update(label="Mission Logic Compiled!", state="complete", expanded=False)
            
            # Show the "Brain" Logic
            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.info("**Extracted Intent**")
                st.json({"action": "SEARCH_DESCEND", "target": "car", "attr": "red"})
            with res_col2:
                st.success("**Navigation Path**")
                st.code("WAYPOINT_A: [45.2, 12.8]\nWAYPOINT_B: [46.1, 13.0]\nMODE: FRONTIER_EXPLORATION")
        else:
            st.warning("Please enter a command first.")

with top_right:
    st.subheader("📸 Vision Feed (Sim)")
    # This acts as a placeholder for your YOLO detections
    st.image("https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&q=80&w=400", caption="HAWK Raw Perception Feed")
    st.metric("Detected Objects", "7", "+2")

st.divider()

# --- BOTTOM SECTION: THE ARCHITECTURE SHOWCASE ---
st.subheader("📂 System Core Exploration")
tab1, tab2, tab3, tab4 = st.tabs(["🧠 Reasoning", "💾 Memory", "🔄 Learning", "📊 Metrics"])

with tab1:
    st.write("### Semantic Reasoning Engine")
    st.write("HAWK uses a cross-dataset reasoning flow to understand environment context.")
    st.code("""
    if target == 'car' and domain == 'urban':
        bias = DIRECTIONAL_SEARCH_ROAD
    elif target == 'car' and domain == 'forest':
        bias = CRASH_PREVENTION_ACTIVE
    """, language="python")

with tab2:
    st.write("### Persistent Memory Datasets")
    # This visualizes the files you have in your 'datasets/' folder
    data = {
        "Dataset": ["Instruction", "Landmark", "Path", "Experience", "Crash"],
        "Entries": [150, 420, 89, 210, 15],
        "Status": ["Synced", "Synced", "Updating", "Synced", "Alert"]
    }
    st.dataframe(pd.DataFrame(data), use_container_width=True)

with tab3:
    st.write("### Phase 2: Domain Adaptation")
    st.write("The ResNet18 backbone extracts signatures from new environments to update the model.")
    if st.button("Trigger Domain Re-Sync"):
        with st.spinner("Analyzing environment signatures..."):
            time.sleep(2)
            st.success("New Domain Detected: 'Industrial_Zone_Beta'. Signature updated.")

with tab4:
    st.write("### Performance Metrics")
    m1, m2, m3 = st.columns(3)
    m1.metric("Coverage %", "94.2%", "+2.1%")
    m2.metric("Collision Rate", "0.02%", "-0.01%")
    m3.metric("Path Efficiency", "88.5%", "+5.4%")

st.balloons()
