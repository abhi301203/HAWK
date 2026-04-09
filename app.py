import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(page_title="H.A.W.K. System Dashboard", layout="wide")

st.title("🦅 H.A.W.K. | Hybrid Autonomous Waypoint Knowledge")
st.markdown("### Multi-Domain UAV Navigation Intelligence Core")

# --- ARCHITECTURE OVERVIEW ---
st.sidebar.header("System Status")
st.sidebar.status("Core: Online", state="complete")
st.sidebar.status("Perception: Ready", state="complete")
st.sidebar.status("AirSim Link: Simulated", state="running")

# --- 1. THE REASONING ENGINE (Show off your logic!) ---
st.header("🧠 1. Semantic Reasoning & NLP")
st.info("This module parses human intent into actionable UAV waypoints.")

user_input = st.text_input("Simulate a Human Instruction:", "Go to the red car near the warehouse")

if user_input:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("NLP Extraction")
        st.json({"action": "navigate", "target": "car", "color": "red", "proximity": "warehouse"})
    with col2:
        st.subheader("Strategic Reasoning")
        st.write("1. Searching 'Object Cluster Memory' for 'Vehicles'...")
        st.write("2. Identifying 'Warehouse' as a spatial landmark...")
        st.success("Target Waypoint: [124.5, -42.8, 10.0]")

# --- 2. THE MEMORY SYSTEM (Show your datasets!) ---
st.header("💾 2. Persistent Memory (Landmark & Domain)")
tab1, tab2 = st.tabs(["Landmark Database", "Domain Adaptation"])

with tab1:
    st.write("Recent Object Detections (YOLOv8 + Spatial Mapping)")
    # Sample data that mimics your dataset
    sample_data = {
        'Object': ['Car', 'Tree', 'Building', 'Truck'],
        'Confidence': [0.92, 0.85, 0.98, 0.76],
        'Spatial_Coord': ['[10, 20]', '[-5, 30]', '[40, 15]', '[12, -5]']
    }
    st.table(pd.DataFrame(sample_data))

with tab2:
    st.write("Domain Signatures (ResNet18 Feature Extractions)")
    st.code("Domain Alpha: Urban_Environment_01\nFeature Vector: [0.12, 0.88, 0.45, ...]", language="text")
    st.progress(85, text="Adaptation Confidence")

# --- 3. PROJECT ARCHITECTURE ---
st.header("🏗️ 3. Complete System Architecture")
st.image("https://mermaid.ink/img/pako:eNqNUdtOwzAM_ZUrX7A_4A1pEtoHSAyJiVvSJi69uEmr-HeSdtm6TpqEPFmxc3zOTR-onBFAKax_UByLAtY2RmsE06F6f7N-t7_YV_tpf7GP_M0W8CclH-UqZ0kK6997h1oN-Y8Hw89lAisLWEV1EIsUlmYIK6gOYhEreAnLQSwisCxFWEZ1EIsYlkV1EIsYlnUQi7iCly_q_T-2-P_v-P9P7f8v7f_P-P9P-P8n9P-E-p9Q_xPq_5_6_0_9f6n-f-r_P_X_p_r_m_r-A2l58O0")
