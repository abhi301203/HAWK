import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# --- RESEARCH IDENTITY ---
st.set_page_config(page_title="H.A.W.K. | Research Portal", page_icon="🦅", layout="wide")

# Custom Professional Styling
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .stCodeBlock { border: 1px solid #30363d; }
    .stAlert { border-left: 5px solid #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# --- SIMULATED DATA (Based on Documentation) ---
# Landmark Memory (Phase 3)
landmark_db = {
    "red car": {"coords": [18, 42], "domain": "Urban", "id": "L-001"},
    "blue tower": {"coords": [5, 12], "domain": "Industrial", "id": "L-002"},
    "warehouse": {"coords": [35, 10], "domain": "Coastal", "id": "L-003"}
}

# --- HEADER & PUBLICATION INFO ---
st.title("🦅 H.A.W.K. Research Console")
st.markdown("### Hybrid Adaptive Waypoint Knowledge for Multi-Domain UAV Navigation")
st.caption("Published in: International Scientific Journal of Engineering and Management (ISJEM)")
st.link_button("📄 View Published Paper (DOI: 10.55041/ISJEM06067)", "https://doi.org/10.55041/ISJEM06067")

st.divider()

# --- MODULE 1: INTERACTIVE COGNITIVE PIPELINE ---
st.header("🧠 1. Cognitive Decision Flow (Start → End)")
st.write("Input a natural language command to see how the H.A.W.K. modules collaborate.")

instruction = st.text_input("Mission Instruction:", "Go near the red car")

if st.button("RUN INTELLIGENCE CORE"):
    # Sequential Workflow (Based on Section 5.5 & 5.13)
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.write("#### Modular Execution Path")
        
        # 5.3 NLP Processor
        with st.status("Step 1: NLP Processing (SpaCy)", expanded=False):
            st.write("Extracting Actions, Objects, and Modifiers...")
            time.sleep(1)
            target = "red car" if "car" in instruction.lower() else "unknown"
            st.success(f"Detected: [Object: {target}] [Action: Go]")
            
        # 5.4 Memory System (Phase 3)
        with st.status("Step 2: Memory Retrieval (Phase 3)", expanded=False):
            st.write("Querying Instruction & Landmark Memories...")
            time.sleep(1)
            found = target in landmark_db
            if found:
                st.info(f"Landmark Found in Memory: {landmark_db[target]['id']} at {landmark_db[target]['coords']}")
            else:
                st.warning("No memory match. Initiating Frontier Exploration.")
                
        # 5.6 Semantic Reasoning
        with st.status("Step 3: Semantic Reasoning Engine", expanded=False):
            st.write("Applying Domain Biases...")
            time.sleep(1)
            if "car" in target:
                st.info("Logic: Object is 'Vehicle'. Bias navigation towards road-structures.")
            
        # 5.11 Domain Adaptation (Phase 2)
        with st.status("Step 4: Domain Adaptation (ResNet18)", expanded=False):
            st.write("Matching environment signatures...")
            time.sleep(1)
            st.success("Environment: Urban. Adjusting weights for urban obstacle density.")
            
    with col2:
        st.write("#### Generated 2D Spatial Waypoints")
        # Visualizing the Waypoint Knowledge
        target_coords = landmark_db[target]['coords'] if target in landmark_db else [25, 25]
        
        fig = go.Figure()
        # Drone Start
        fig.add_trace(go.Scatter(x=[0], y=[0], name="Home", marker=dict(size=12, color='white')))
        # Waypoints
        fig.add_trace(go.Scatter(x=[0, target_coords[0]], y=[0, target_coords[1]], 
                                 mode='lines+markers', name="Flight Path", line=dict(color='cyan', dash='dot')))
        # Target
        fig.add_trace(go.Scatter(x=[target_coords[0]], y=[target_coords[1]], 
                                 mode='markers+text', name="Target Waypoint", 
                                 text=["TARGET"], textposition="top center", marker=dict(size=15, color='red')))
        
        fig.update_layout(template="plotly_dark", xaxis_title="X-Axis (m)", yaxis_title="Y-Axis (m)", height=400)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- MODULE 2: REASONING & LEARNING ANALYSIS ---
st.header("📊 2. Continuous Learning & Data Analytics")
tab1, tab2, tab3 = st.tabs(["💾 Landmark Memory", "🔄 Domain Fingerprints", "📈 Performance Logs"])

with tab1:
    st.write("#### Phase 3: Spatial Graph Memory")
    st.write("The system stores discovered landmarks to avoid redundant exploration.")
    df_landmarks = pd.DataFrame.from_dict(landmark_db, orient='index')
    st.table(df_landmarks)

with tab2:
    st.write("#### Phase 2: ResNet18 Signature Extraction")
    st.write("Feature vector visualization from high-dimensional environment embeddings.")
    # Real random distribution mimicking ResNet18 feature vectors
    feature_vec = np.random.randn(64)
    st.bar_chart(feature_vec)
    st.caption("Signature: 0x8F2... (Urban Environment)")

with tab3:
    st.write("#### System Efficiency (Multi-Domain Testing)")
    # Metrics from your report
    m1, m2, m3 = st.columns(3)
    m1.metric("Coverage %", "94.2", "+2.5")
    m2.metric("Target Success", "89.1%", "+4.2")
    m3.metric("Adaptation Latency", "124ms", "-12ms")

# --- ARCHITECTURE MODAL ---
st.divider()
st.subheader("🏗️ Full System Architecture (Reference)")
# Using your official Architecture diagram from the document
st.image("https://raw.githubusercontent.com/YourGitHubUsername/YourRepo/main/architecture_diagram.png", caption="Fig 4.1: H.A.W.K System Architecture")

st.info("**Research Conclusion:** H.A.W.K. allows UAVs to generalize across multiple unseen domains such as urban and rural without requiring retraining. [cite: 54, 578]")
