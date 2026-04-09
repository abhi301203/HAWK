import streamlit as st
import pandas as pd
import numpy as np
import time
from ai_logic import HAWK_Sovereign_Engine
from world_engine import render_sovereign_map, ENVIRONMENT_CONFIG

# --- IDEA 1: COMMAND & CONTROL ---
st.set_page_config(page_title="HAWK SOVEREIGN HUB", layout="wide")
st.markdown("""
    <style>
    .block-container { padding: 1rem 5rem !important; background-color: #000; }
    h1 { color: #00FF41; font-family: 'Courier New'; letter-spacing: 10px; text-shadow: 0 0 10px #00FF41; }
    .stMetric { border: 1px solid #00FF41 !important; background: rgba(0,255,65,0.05); }
    </style>
    """, unsafe_allow_html=True)

# Session State Initialization
if 'engine' not in st.session_state: st.session_state.engine = HAWK_Sovereign_Engine()
if 'pos' not in st.session_state: st.session_state.pos = [2, 2]
if 'knowledge_base' not in st.session_state: st.session_state.knowledge_base = []

# --- TOP HUD: SYSTEM TELEMETRY ---
st.title("🦅 H.A.W.K. SOVEREIGN MISSION HUB")
st.divider()

m1, m2, m3, m4 = st.columns(4)
m1.metric("GLOBAL_POS", f"{st.session_state.pos}")
m2.metric("NEURAL_CONFIDENCE", "0.982", "+0.001")
m3.metric("SYNESTHESIA_SYNC", "STABLE")
m4.metric("SWARM_PEERS", "14 Active")

# --- MAIN OPERATION CENTER ---
col_map, col_intel = st.columns([3, 1.5])

with col_map:
    map_view = st.empty()
    map_view.plotly_chart(render_sovereign_map(st.session_state.pos, {'x':[], 'y':[]}, {'x':[], 'y':[]}, []), use_container_width=True)
    
    # Idea 12 & 17: Signal HUD
    c1, c2 = st.columns(2)
    with c1:
        st.write("📡 Idea 12: Synesthesia Signal Stream")
        st.line_chart(st.session_state.engine.compute_synesthesia_signals(), height=150)
    with c2:
        st.write("🧬 Idea 8: Neural DNA Extract (ResNet18)")
        st.bar_chart(st.session_state.engine.get_neural_dna()[:64], height=150)

with col_intel:
    st.subheader("📟 Intelligence Console")
    # Idea 14: Human Telepathy
    cmd = st.text_input("INPUT NEURAL INSTRUCTION:", "Navigate to Hospital")
    
    if st.button("▶ INITIATE MISSION"):
        # Idea 3: Reasoning Step-Through
        meta = st.session_state.engine.process_vln_instruction(cmd)
        
        with st.status("Engine State: COGNITIVE_INFERENCE...", expanded=True) as status:
            st.write(f"`[NLP]` UUID: {meta['UUID']} | Target: {meta['TARGET_NODE']}")
            st.write(f"`[MEM]` Searching Spatial Graph Layer...")
            
            target = next((n for n in ENVIRONMENT_CONFIG["nodes"] if n["name"].startswith(meta["TARGET_NODE"][:3])), None)
            
            if target:
                hx, hy, gx, gy = st.session_state.engine.calculate_stochastic_path(st.session_state.pos, target['pos'])
                
                # The 'Impossible' Loop: Smooth Traversal (Idea 16)
                for i in range(len(hx)):
                    st.session_state.pos = [hx[i], hy[i]]
                    
                    # Idea 5 & 13: Online Learning & Swarm Sync
                    for node in ENVIRONMENT_CONFIG["nodes"]:
                        dist = np.sqrt((hx[i]-node['pos'][0])**2 + (hy[i]-node['pos'][1])**2)
                        if dist < 6 and node['name'] not in [k['node'] for k in st.session_state.knowledge_base]:
                            sync_data = st.session_state.engine.sync_global_ledger(node['name'])
                            st.session_state.knowledge_base.append(sync_data)
                            st.toast(f"SYNC: {node['name']} SHARED TO SWARM")

                    # Update Digital Twin
                    map_view.plotly_chart(render_sovereign_map([hx[i], hy[i]], {'x':hx[:i], 'y':hy[:i]}, {'x':gx[:i], 'y':gy[:i]}, []), use_container_width=True, key=f"mission_{i}")
                    time.sleep(0.01)
                
                status.update(label="MISSION_SUCCESS: TARGET_LOCKED", state="complete")

# --- BOTTOM LOG: IDEA 9: PERFORMANCE BLACK BOX ---
st.divider()
st.subheader("📂 Idea 9: Sovereign Knowledge Ledger (Phase 3 Memory)")
if st.session_state.knowledge_base:
    st.table(pd.DataFrame(st.session_state.knowledge_base))
