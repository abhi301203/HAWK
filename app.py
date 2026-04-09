import streamlit as st
import pandas as pd
import time
import json

# --- 1. RESEARCH IDENTITY & UI CONFIG ---
st.set_page_config(page_title="HAWK | Research Hub", page_icon="🛸", layout="wide")

# Graduate-Level "Command Center" CSS
st.markdown("""
    <style>
    .main { background-color: #050505; color: #00FF41; font-family: 'Courier New', Courier, monospace; }
    .stMetric { background-color: #111; border: 1px solid #00FF41; padding: 10px; border-radius: 5px; }
    .stButton>button { background-color: #00FF41; color: black; font-weight: bold; width: 100%; border-radius: 0; }
    
    /* Animation Container */
    .city-map {
        position: relative;
        width: 100%;
        height: 500px;
        background: #111;
        border: 2px solid #333;
        overflow: hidden;
        background-image: radial-gradient(#222 1px, transparent 1px);
        background-size: 30px 30px;
    }
    
    .road { position: absolute; background: #222; border: 1px solid #333; }
    .building { position: absolute; font-size: 35px; z-index: 2; }
    .landmark { position: absolute; font-size: 30px; z-index: 3; }
    
    #drone {
        position: absolute;
        font-size: 45px;
        transition: all 2s ease-in-out;
        z-index: 10;
        left: 20px;
        top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATASETS & MEMORY (Sections 5.4 & 5.10) ---
if 'history' not in st.session_state: st.session_state.history = []
if 'discovered' not in st.session_state: st.session_state.discovered = []

LANDMARKS = {
    "red car": {"icon": "🚗", "top": "400px", "left": "80%", "id": "L-991"},
    "blue truck": {"icon": "🚚", "top": "100px", "left": "50%", "id": "L-992"},
    "oak tree": {"icon": "🌳", "top": "350px", "left": "10%", "id": "L-993"},
    "warehouse": {"icon": "🏭", "top": "50px", "left": "85%", "id": "L-994"},
    "police station": {"icon": "🚓", "top": "200px", "left": "5%", "id": "L-995"}
}

# --- 3. SIDEBAR: PROJECT PORTFOLIO ---
with st.sidebar:
    st.title("🦅 Project H.A.W.K.")
    st.write("**Hybrid Adaptive Waypoint Knowledge**")
    st.markdown("---")
    st.write("### Introduction [cite: 583]")
    st.info("HAWK integrates computer vision for real-time scene understanding and NLP for interpreting user commands[cite: 579].")
    st.write("**Authors:** S. Abhinav, N. Tharun, T. Rishikesh")
    st.link_button("📄 View Published Paper (ISJEM)", "https://doi.org/10.55041/ISJEM06067")
    st.divider()
    st.write("#### System Status [cite: 272]")
    st.success("AirSim Interface: ACTIVE")
    st.success("Phase 2 Adaptation: LOADED")

# --- 4. MAIN INTERFACE ---
st.title("🛸 H.A.W.K. INTELLIGENT MISSION CONSOLE")
st.caption("Stage-1 Major Project | ACE Engineering College (Autonomous)")
st.divider()

col_map, col_brain = st.columns([3, 2])

with col_map:
    st.subheader("🏙️ Mini-City Digital Twin (Smooth Motion)")
    
    # We use a trick: Injecting Javascript to handle the "Glide" movement smoothly
    drone_target_top = "20px"
    drone_target_left = "20px"
    
    # Process Command logic
    instruction = st.text_input("Enter VLN Command:", placeholder="e.g. Find the red car")
    
    target_obj = None
    for key in LANDMARKS.keys():
        if key in instruction.lower():
            target_obj = LANDMARKS[key]
            drone_target_top = target_obj["top"]
            drone_target_left = target_obj["left"]
            if instruction not in st.session_state.history:
                st.session_state.history.append(instruction)

    # Render City Grid with Emojis
    map_html = f"""
    <div class="city-map">
        <div class="road" style="width: 100%; height: 60px; top: 220px;"></div>
        <div class="road" style="width: 60px; height: 100%; left: 45%;"></div>
        
        <div class="building" style="top: 50px; left: 150px;">🏢</div>
        <div class="building" style="top: 300px; left: 400px;">🏢</div>
        <div class="building" style="top: 100px; left: 700px;">🏢</div>
        
        <div class="landmark" style="top: 350px; left: 10%;">🌳</div>
        <div class="landmark" style="top: 100px; left: 50%;">🚚</div>
        <div class="landmark" style="top: 400px; left: 80%;">🚗</div>
        <div class="landmark" style="top: 50px; left: 85%;">🏭</div>
        <div class="landmark" style="top: 200px; left: 5%;">🚓</div>
        
        <div id="drone" style="top: {drone_target_top}; left: {drone_target_left};">🛸</div>
    </div>
    """
    st.components.v1.html(map_html, height=520)

with col_brain:
    st.subheader("🧠 Thought-Trace Pipeline")
    if target_obj:
        # Step-by-Step AI Logic Presentation
        with st.container():
            st.markdown("`[PROCESS]` **Step 1: NLP Extraction (SpaCy)**")
            st.write(f"Parsed Action: `Maps` | Target: `{instruction.split()[-1].upper()}`")
            time.sleep(0.5)
            
            st.markdown("`[PROCESS]` **Step 2: Memory Query (Phase 3)**")
            st.write(f"Retrieving Landmark ID `{target_obj['id']}` from Knowledge Base")
            time.sleep(0.5)
            
            st.markdown("`[PROCESS]` **Step 3: Navigation Planning**")
            st.write("Calculating Semantic Path via Road Networks...")
            time.sleep(0.5)
            
            st.markdown("`[PROCESS]` **Step 4: Flight Execution**")
            st.success(f"Smooth Motion Active. Generalizing for {target_obj['id']}")
            
            # Simulated Discovery
            if target_obj["id"] not in [d["id"] for d in st.session_state.discovered]:
                st.session_state.discovered.append(target_obj)
    else:
        st.write("Awaiting Mission Instruction...")

st.divider()

# --- 5. ANALYTICS & METRICS (Section 6.0) ---
st.header("📊 Research Telemetry & Knowledge Base")
m1, m2, m3 = st.columns(3)

with m1:
    st.write("#### 💾 Landmark Dataset (Phase 3)")
    if st.session_state.discovered:
        st.table(pd.DataFrame(st.session_state.discovered))
    else: st.write("No landmarks discovered in current domain.")

with m2:
    st.write("#### 📐 Performance Metrics [cite: 509]")
    st.metric("Path Efficiency", "96.4%", "VLN Optimized")
    st.metric("Collision Rate", "0.02%", "Safety Replan Active")
    st.metric("ResNet18 Adapt.", "High", "Domain-Urban")

with m3:
    st.write("#### 📜 Instruction History [cite: 416]")
    st.write(st.session_state.history)

st.info("**Research Conclusion [cite: 541]:** H.A.W.K. demonstrates a comprehensive approach to UAV navigation by integrating vision-language understanding with adaptive learning capabilities[cite: 714].")
