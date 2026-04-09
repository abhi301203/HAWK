import streamlit as st
import pandas as pd
import numpy as np
import time
from interface_style import apply_custom_style
from world_engine import build_4d_environment, CITY_DATA
from ai_logic import HAWKCore

# Initialize 
apply_custom_style()
if 'hawk' not in st.session_state: st.session_state.hawk = HAWKCore()
if 'pos' not in st.session_state: st.session_state.pos = [2, 2]
if 'memory' not in st.session_state: st.session_state.memory = []
if 'hazards' not in st.session_state: st.session_state.hazards = []

# --- IDEA 1: COMMAND & CONTROL HUD ---
st.markdown("<div class='hud-header'><h1>🦅 H.A.W.K. SOVEREIGN INTELLIGENCE HUB</h1></div>", unsafe_allow_html=True)

# Layout
col_telemetry, col_sim, col_intel = st.columns([1, 3, 1.5])

with col_telemetry:
    st.subheader("📡 Telemetry")
    st.metric("ALTITUDE", "120m", "SAFE")
    st.metric("LATENCY", f"{np.random.randint(8, 15)}ms", "-2ms")
    st.metric("SWARM_SYNC", "ONLINE")
    
    # Idea 12: Synesthesia stream
    st.write("🛰️ Synesthesia Frequency")
    st.line_chart(st.session_state.hawk.get_synesthesia_frequencies(), height=100)
    
    # Idea 14: Emergency Telepathy
    if st.button("🚨 MANUAL OVERRIDE"):
        st.toast("HUMAN_INTERRUPT: Re-calculating safety weights...")

with col_sim:
    map_placeholder = st.empty()
    # Initial Map
    fig = build_4d_environment(st.session_state.pos, {'x':[], 'y':[]}, {'x':[], 'y':[]}, st.session_state.hazards)
    map_placeholder.plotly_chart(fig, use_container_width=True)
    
    # Idea 8: ResNet DNA HUD
    st.write("🧬 ResNet18 Neural DNA Signature")
    st.bar_chart(st.session_state.hawk.get_resnet_dna(), height=150)

with col_intel:
    st.subheader("🧠 Intelligence Logic")
    # Idea 6: Thought Trace
    prompt = st.text_input("INPUT NEURAL INSTRUCTION:", "Go to hospital")
    
    if st.button("▶ EXECUTE MISSION"):
        trace = st.session_state.hawk.extract_thought_trace(prompt)
        
        with st.container():
            st.markdown("<div class='terminal-box'>", unsafe_allow_html=True)
            st.write(f"`[SYSTEM]` Parsing: {trace['entities']}")
            st.write(f"`[SYSTEM]` Decision: {trace['decision']}")
            st.write(f"`[SYSTEM]` Swarm Syncing...")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Find target
            target = next((l for l in CITY_DATA["landmarks"] if l["name"].lower().startswith(trace['entities'][0][:3])), None)
            
            if target:
                # Idea 16 & 15: Compute trajectories
                px, py, gx, gy = st.session_state.hawk.compute_path(st.session_state.pos, target['pos'])
                
                # Simulation Loop
                for i in range(len(px)):
                    st.session_state.pos = [px[i], py[i]]
                    
                    # Idea 5: Online Discovery
                    for lm in CITY_DATA["landmarks"]:
                        dist = np.sqrt((px[i]-lm['pos'][0])**2 + (py[i]-lm['pos'][1])**2)
                        if dist < 5 and lm['name'] not in [m['name'] for m in st.session_state.memory]:
                            st.session_state.memory.append(lm)
                            st.toast(st.session_state.hawk.sync_global_ledger(lm['name']))

                    # Render
                    fig = build_4d_environment([px[i], py[i]], {'x':px[:i], 'y':py[:i]}, 
                                               {'x':gx[:i], 'y':gy[:i]}, st.session_state.hazards)
                    map_placeholder.plotly_chart(fig, use_container_width=True, key=f"mission_{i}")
                    time.sleep(0.01)
                
                st.success("TARGET_REACHED: Navigation Complete.")

# Idea 9: Black Box DVR Memory
st.divider()
st.subheader("📂 Idea 9: Performance Black Box (Persistent Knowledge)")
if st.session_state.memory:
    st.table(pd.DataFrame(st.session_state.memory))
