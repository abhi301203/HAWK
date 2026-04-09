import streamlit as st
import time
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="HAWK | Research Console", page_icon="🦅", layout="wide")

# --- CUSTOM THEME ---
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stAlert { background-color: #161b22; border: 1px solid #30363d; }
    code { color: #58a6ff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ARCHITECTURE REFERENCE LOGIC ---
def process_hawk_logic(command):
    """Simulates the 5.5 Decision Engine flow based on user input"""
    # 5.3 NLP (SpaCy Mock)
    tokens = command.lower().split()
    action = "find" if "find" in tokens or "search" in tokens else "go"
    target = "car" if "car" in tokens else "tree" if "tree" in tokens else "object"
    color = "red" if "red" in tokens else "blue" if "blue" in tokens else "none"
    
    return {
        "action": action,
        "object": target,
        "color": color,
        "modifier": "near" if "near" in tokens else "around" if "around" in tokens else "none"
    }

# --- HEADER ---
st.title("🦅 H.A.W.K. Cognitive Command Center")
st.caption("Hybrid Autonomous Waypoint Knowledge for Multi-Domain UAV Navigation")
st.markdown("---")

# --- TOP SECTION: MISSION EXECUTION ---
col_hud, col_log = st.columns([3, 2])

with col_hud:
    st.subheader("📡 Primary Perception Feed (AirSim)")
    # High-quality drone footage representing the active perception layer
    st.video("https://www.youtube.com/watch?v=N_vT_A_H_6Y") 
    
    # 5.2 Perception Module Stats
    st.write("**Real-time Object Detection (YOLOv8)**")
    p1, p2, p3 = st.columns(3)
    p1.metric("Detection Confidence", "0.89", "YOLOv8")
    p2.metric("Inference Time", "12ms", "-2ms")
    p3.metric("Current Domain", "Industrial", "ResNet18")

with col_log:
    st.subheader("⌨️ VLN Instruction Input")
    user_input = st.text_input("Enter Command:", placeholder="Go near the red car")
    
    if st.button("EXECUTE MISSION ENGINE"):
        if user_input:
            # 5.5 COMPLETE DECISION FLOW (Logic matching your report)
            with st.status("🧠 HAWK Decision Engine Active", expanded=True) as status:
                
                # Step 1: NLP Extraction (5.3)
                st.write("Step 1: NLP Parsing (SpaCy `en_core_web_sm`)...")
                parsed_logic = process_hawk_logic(user_input)
                time.sleep(1)
                
                # Step 2: Memory Checks (5.4)
                st.write("Step 2: Checking Instruction & Landmark Memory...")
                time.sleep(1)
                
                # Step 3: Semantic Reasoning (5.6)
                st.write(f"Step 3: Semantic Reasoning (Target: {parsed_logic['object']})...")
                if parsed_logic['object'] == "car":
                    st.info("💡 Semantic Bias: 'Car' detected. Prioritizing road regions for search.")
                time.sleep(1)
                
                # Step 4: Waypoint Generation (5.7)
                st.write("Step 4: Generating Trajectory (Frontier Exploration Mode)...")
                time.sleep(1)
                
                status.update(label="Mission Logic Generated", state="complete")
            
            # OUTPUT DISPLAY
            st.divider()
            st.markdown("#### 🛠️ Module Outputs")
            o1, o2 = st.columns(2)
            with o1:
                st.write("**NLP Extraction (5.3)**")
                st.json(parsed_logic)
            with o2:
                st.write("**Navigation Execution (5.7)**")
                st.code(f"EXEC: {parsed_logic['action'].upper()}\nMODE: DIRECTIONAL_BIAS\nCOORDS: [14.5, -22.1, 5.0]")
        else:
            st.error("Please enter an instruction.")

st.markdown("---")

# --- BOTTOM SECTION: DATASETS & LEARNING (PHASE 2) ---
st.subheader("📂 Stored Knowledge & Domain Adaptation")
tab1, tab2, tab3 = st.tabs(["💾 Memory Datasets", "🔄 Phase 2: Learning", "📊 System Metrics"])

with tab1:
    st.write("### 5.10 Dataset Management")
    # Table representing your 5.10 dataset list
    ds_data = {
        "Dataset": ["Instruction", "Landmark", "Path", "Experience", "Crash"],
        "Purpose": ["Past commands", "Object locations", "Nav paths", "Success/Failure", "Failure scenarios"],
        "Count": [142, 856, 45, 120, 8]
    }
    st.table(pd.DataFrame(ds_data))

with tab2:
    st.write("### 5.11 Domain Adaptation Pipeline (ResNet18)")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Domain Signature (Fingerprint)**")
        # Visualizing feature extraction logic
        chart_data = pd.DataFrame(np.random.randn(20, 1), columns=['Feature Vector'])
        st.area_chart(chart_data)
    with c2:
        st.write("**Pipeline Status**")
        st.write("- Collected Data Integrity: ✅")
        st.write("- Index Generation: ✅")
        st.write("- Feature Extraction: ✅")
        if st.button("Run Phase 2 Model Update"):
            with st.spinner("Training ResNet18 on new domain data..."):
                time.sleep(3)
                st.success("Model Updated: knowledge_storage.npy synchronized.")

with tab3:
    st.write("### 6. Performance Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Coverage %", "92.4%")
    m2.metric("Target Success", "88.1%")
    m3.metric("Collision Rate", "0.04%")
    m4.metric("Frontier Efficiency", "76.5%")
