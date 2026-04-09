import streamlit as st
import pandas as pd
from assets import create_world_view, CITY_ASSETS
from engine import calculate_traversal, run_cognitive_cycle, sync_to_swarm

# IDEA 1: COMMAND & CONTROL INTERFACE
st.set_page_config(page_title="HAWK MISSION CONTROL", layout="wide")

# CSS for a Professional Research Environment
st.markdown("<style>.stApp { background: #000; color: #00FF41; }</style>", unsafe_allow_html=True)

# SIDEBAR: SANDBOX CONTROLS
with st.sidebar:
    st.title("🦅 H.A.W.K. PORTAL")
    # IDEA 11: RECURSIVE SANDBOX
    if st.button("♻️ Reset AI Knowledge"): st.rerun()
    # IDEA 10 & 14: STRESS TEST & OVERRIDE
    stress_mode = st.toggle("🚧 Idea 10: Inject Static Hazards")
    # IDEA 13: GLOBAL SYNC STATUS
    st.status("Global Swarm: CONNECTED")

# MAIN HUD
st.title("🛸 H.A.W.K. INTELLIGENCE HUD")
col_map, col_data = st.columns([3, 2])

# Initialization
if 'pos' not in st.session_state: st.session_state.pos = [25, 2]
if 'mem' not in st.session_state: st.session_state.mem = []

with col_map:
    # IDEA 12: CROSS-MODAL SYNESTHESIA (Signal Visualizer)
    st.subheader("📡 Idea 12: Neural Signal Stream")
    st.line_chart(np.random.randn(20, 2), height=150)
    
    map_box = st.empty()
    map_box.plotly_chart(create_world_view(st.session_state.pos, None, None, None, None, stress_mode), use_container_width=True)

with col_data:
    # IDEA 6 & 8: THOUGHT TRACE & DOMAIN HUD
    st.subheader("🧠 Idea 8: Domain Adaptation HUD")
    st.progress(0.92, text="ResNet18 Match: URBAN_DOMAIN")
    
    cmd = st.text_input("INPUT VLN INSTRUCTION:", placeholder="Go to hospital")
    
    if st.button("▶ INITIATE MISSION"):
        # IDEA 3 & 6: Run AI Logic
        with st.status("Thinking...", expanded=True) as s:
            logic_logs = run_cognitive_cycle(cmd)
            for log in logic_logs: st.write(log)
            
            # Find destination
            target = next((b for b in CITY_ASSETS["infrastructure"]["buildings"] if b["name"].lower() in cmd.lower()), None)
            
            if target:
                # IDEA 16: Traverse (High Res)
                tx, ty, gx, gy = calculate_traversal(st.session_state.pos, target["pos"])
                
                for i in range(len(tx)):
                    st.session_state.pos = [tx[i], ty[i]]
                    # IDEA 5: ONLINE SYNC
                    if i % 30 == 0:
                        sync_msg = sync_to_swarm(target)
                        st.toast(sync_msg)
                    
                    # IDEA 15: GHOST PATH (Showing the comparison)
                    map_box.plotly_chart(create_world_view([tx[i], ty[i]], tx[:i], ty[:i], gx[:i], gy[:i], stress_mode), 
                                         use_container_width=True, key=f"f_{i}")
                
                # IDEA 9: PERFORMANCE BLACK BOX (Save to Memory)
                if target not in st.session_state.mem: st.session_state.mem.append(target)
                s.update(label="MISSION SUCCESS", state="complete")

# IDEA 9: KNOWLEDGE TABLE
st.divider()
st.header("📊 Idea 9: Performance Black Box (Persistent Memory)")
st.table(pd.DataFrame(st.session_state.mem) if st.session_state.mem else pd.DataFrame(columns=["name", "pos", "icon", "desc"]))
