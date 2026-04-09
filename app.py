import streamlit as st
import pandas as pd
import numpy as np  # <--- THIS FIXES THE NAMEERROR
import time
from assets import create_world_view, CITY_ASSETS
from engine import calculate_traversal, run_cognitive_cycle, sync_to_swarm

# IDEA 1: COMMAND & CONTROL INTERFACE
st.set_page_config(page_title="HAWK MISSION CONTROL", layout="wide")
st.markdown("<style>.stApp { background: #000; color: #00FF41; }</style>", unsafe_allow_html=True)

# Session State for Idea 7 & 11
if 'pos' not in st.session_state: st.session_state.pos = [25, 2]
if 'mem' not in st.session_state: st.session_state.mem = []

with st.sidebar:
    st.title("🦅 H.A.W.K. PORTAL")
    st.info("Hybrid Autonomous Waypoint Knowledge")
    # IDEA 11: RECURSIVE SANDBOX
    if st.button("♻️ Reset AI Knowledge"): 
        st.session_state.mem = []
        st.rerun()
    # IDEA 10 & 14: STRESS TEST & OVERRIDE
    stress_mode = st.toggle("🚧 Idea 10: Inject Static Hazards")
    st.markdown("---")
    st.caption("DOI: 10.55041/ISJEM06067")

col_map, col_data = st.columns([3, 2])

with col_map:
    # IDEA 12: CROSS-MODAL SYNESTHESIA HUD
    st.subheader("📡 Idea 12: Cross-Modal Signal Stream")
    st.line_chart(np.random.randn(20, 2), height=150) 
    
    map_box = st.empty()
    map_box.plotly_chart(create_world_view(st.session_state.pos, None, None, None, None, stress_mode), use_container_width=True)

with col_data:
    # IDEA 8: DOMAIN ADAPTATION HUD (Neural DNA)
    st.subheader("🧬 Idea 8: Domain Adaptation HUD")
    st.bar_chart(np.random.rand(32), height=150)
    st.caption("Active Signature: ResNet18_Urban_Phase2")
    
    # IDEA 13: GLOBAL SWARM SYNC STATUS
    st.status("Global Swarm Knowledge Sync: ACTIVE")
    
    cmd = st.text_input("INPUT VLN INSTRUCTION:", placeholder="e.g. Go to hospital")
    
    if st.button("▶ INITIATE H.A.W.K. ENGINE"):
        with st.status("Thinking...", expanded=True) as s:
            # IDEA 3 & 6: COGNITIVE PIPELINE & THOUGHT-TRACE
            logs = run_cognitive_cycle(cmd)
            for l in logs: st.write(l)
            
            target = next((b for b in CITY_ASSETS["infrastructure"]["buildings"] if b["name"].lower() in cmd.lower()), None)
            
            if target:
                # IDEA 16: STOCHASTIC PATHFINDING (X10 Resolution)
                tx, ty, gx, gy = calculate_traversal(st.session_state.pos, target["pos"])
                for i in range(len(tx)):
                    st.session_state.drone_pos_internal = [tx[i], ty[i]]
                    
                    # IDEA 15: GHOST PATH Comparison
                    # Rendering HAWK path (Green) vs Non-Adaptive path (Red)
                    map_box.plotly_chart(create_world_view([tx[i], ty[i]], tx[:i], ty[:i], gx[:i], gy[:i], stress_mode), 
                                         use_container_width=True, key=f"f_{i}")
                    time.sleep(0.01)
                
                # Update Session position after flight
                st.session_state.pos = [tx[-1], ty[-1]]
                
                # IDEA 9: PERFORMANCE BLACK BOX (Knowledge Sync)
                if target not in st.session_state.mem: st.session_state.mem.append(target)
                s.update(label="MISSION SUCCESS", state="complete")

st.divider()
st.header("📊 Idea 9: Performance Black Box (Persistent Memory Table)")
st.table(pd.DataFrame(st.session_state.mem) if st.session_state.mem else pd.DataFrame(columns=["name", "pos", "icon", "desc"]))
