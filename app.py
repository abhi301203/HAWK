import streamlit as st
import pandas as pd
import numpy as np
import time
from interface_style import apply_custom_style
from world_engine import build_mission_map, ENV_DATA
from ai_logic import HAWK_Intelligence

# --- 1. INITIALIZATION ---
apply_custom_style()

# Fix for AttributeError: Ensure engine is persistent
if 'engine' not in st.session_state:
    st.session_state.engine = HAWK_Intelligence()
if 'pos' not in st.session_state:
    st.session_state.pos = [2, 2]
if 'local_memory' not in st.session_state:
    st.session_state.local_memory = []

# --- 2. HEADER HUD ---
st.markdown("## 🦅 H.A.W.K. MISSION CONTROL v3.0")
st.caption("Strategic Intelligence Hub | Patent-Pending Architecture")

# --- 3. DASHBOARD LAYOUT ---
col_map, col_intel = st.columns([2, 1])

with col_map:
    # Idea 10: Sidebar controls moved to main for mobile visibility
    hazard_toggle = st.toggle("🚧 Idea 10: Stress-Tester (Obstacle Injection)")
    
    map_box = st.empty()
    map_box.plotly_chart(build_mission_map(st.session_state.pos, [], [], [], [], hazard_toggle), use_container_width=True)
    
    # Idea 17: Multi-Spectral HUD (Compact Row)
    st.write("📡 Idea 17: Multi-Spectral Vision Filters")
    v1, v2, v3 = st.columns(3)
    v1.image(st.session_state.engine.get_vision_telemetry(), caption="DEPTH", use_container_width=True)
    v2.image(st.session_state.engine.get_vision_telemetry(), caption="IR", use_container_width=True)
    v3.image(st.session_state.engine.get_vision_telemetry(), caption="SEMANTIC", use_container_width=True)

with col_intel:
    st.subheader("🧠 Intelligence Hub")
    
    # Idea 6: Thought-Trace
    instruction = st.text_input("INPUT MISSION COMMAND:", "Go to University")
    
    if st.button("▶ LAUNCH MISSION ENGINE"):
        # Idea 2: Latency
        with st.status("Engine Reasoning...", expanded=True) as status:
            st.markdown("<div class='terminal-text'>[NLP] Extraction: SUCCESS<br>[MEM] Querying Graph...</div>", unsafe_allow_html=True)
            time.sleep(1)
            
            # Find Target
            target = next((l for l in ENV_DATA["landmarks"] if l["name"].lower().startswith(instruction.lower()[:3])), None)
            
            if target:
                px, py, gx, gy = st.session_state.engine.generate_path(st.session_state.pos, target["pos"])
                
                # Idea 16: Smooth Traversal Loop
                for i in range(len(px)):
                    st.session_state.pos = [px[i], py[i]]
                    
                    # Idea 5 & 13: Online Sync
                    for lm in ENV_DATA["landmarks"]:
                        dist = np.sqrt((px[i]-lm["pos"][0])**2 + (py[i]-lm["pos"][1])**2)
                        if dist < 6 and lm["name"] not in [m["landmark"] for m in st.session_state.local_memory]:
                            sync_entry = st.session_state.engine.sync_global(lm["name"])
                            st.session_state.local_memory.append(sync_entry)

                    # Update Map
                    map_box.plotly_chart(build_mission_map([px[i], py[i]], px[:i], py[:i], gx[:i], gy[:i], hazard_toggle), use_container_width=True, key=f"f_{i}")
                    time.sleep(0.01)
                
                status.update(label="MISSION SUCCESS", state="complete")

# --- 4. DATA & ANALYTICS ---
st.divider()
st.subheader("📂 Idea 9: Sovereign Knowledge Ledger")
st.table(pd.DataFrame(st.session_state.local_memory) if st.session_state.local_memory else pd.DataFrame(columns=["id", "landmark", "timestamp"]))

# Idea 8: ResNet DNA DNA HUD
st.write("🧬 Neural Signature DNA (ResNet18)")
st.bar_chart(st.session_state.engine.resnet_signature[:64], height=150)
