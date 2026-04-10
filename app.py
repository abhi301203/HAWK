import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import time
import pandas as pd

# -----------------------------
# INIT FUNCTIONS
# -----------------------------
def init_state():
    st.session_state.drone = {"x": 10, "y": 10}
    st.session_state.path = [(10, 10)]
    st.session_state.hazards = []
    st.session_state.logs = []
    st.session_state.running = False
    st.session_state.target = None

    st.session_state.metrics = {
        "hazards": 0,
        "avoided": 0,
        "near": 0
    }

    st.session_state.landmarks = []

# -----------------------------
# INITIAL LOAD
# -----------------------------
if "init" not in st.session_state:
    st.session_state.init = True

    st.session_state.city = []
    types = [
        "home","hospital","school","church","hotel",
        "tree","garden","pool","car","truck","human","dog"
    ]

    for _ in range(50):
        st.session_state.city.append({
            "x": random.randint(5, 95),
            "y": random.randint(5, 95),
            "type": random.choice(types)
        })

    init_state()

# -----------------------------
# ICONS
# -----------------------------
def icon(t):
    return {
        "home":"🏠","hospital":"🏥","school":"🏫","church":"⛪","hotel":"🏨",
        "tree":"🌳","garden":"🌿","pool":"🏊",
        "car":"🚗","truck":"🚛",
        "human":"🧍","dog":"🐕"
    }.get(t,"❓")

# -----------------------------
# LOGGER
# -----------------------------
def log(msg):
    st.session_state.logs.insert(0, msg)

# -----------------------------
# NLP PARSER
# -----------------------------
def parse(cmd):
    tokens = cmd.lower().split()
    log(f"🧠 Tokens: {tokens}")

    for t in tokens:
        for obj in st.session_state.city:
            if t == obj["type"]:
                log(f"🎯 Target identified: {t}")
                return obj

    return None

# -----------------------------
# DISTANCE
# -----------------------------
def dist(a,b):
    return np.linalg.norm(np.array(a)-np.array(b))

# -----------------------------
# SAFE NAVIGATION
# -----------------------------
def compute_next(pos, target):
    pos = np.array(pos)
    target = np.array(target)

    direction = target - pos
    direction = direction / (np.linalg.norm(direction)+1e-6)

    for h in st.session_state.hazards:
        hpos = np.array([h["x"], h["y"]])
        d = dist(pos, hpos)

        if d < 10:
            repulse = pos - hpos
            repulse = repulse / (d+1e-6)
            direction += repulse * (10/d)

            st.session_state.metrics["near"] += 1
            log("⚠️ Hazard nearby")

        if d < 5:
            st.session_state.metrics["avoided"] += 1
            log("🚧 Avoidance activated")

    direction = direction / (np.linalg.norm(direction)+1e-6)
    new_pos = pos + direction * 1.5

    return tuple(new_pos)

# -----------------------------
# LANDMARK MEMORY UPDATE
# -----------------------------
def update_landmarks(pos):
    for obj in st.session_state.city:
        d = dist(pos, (obj["x"], obj["y"]))
        if d < 3:
            entry = {
                "Type": obj["type"],
                "X": obj["x"],
                "Y": obj["y"],
                "Time": time.strftime("%H:%M:%S")
            }
            if entry not in st.session_state.landmarks:
                st.session_state.landmarks.append(entry)
                log(f"📍 Landmark recorded: {obj['type']}")

# -----------------------------
# UPDATE DRONE
# -----------------------------
def update():
    pos = (st.session_state.drone["x"], st.session_state.drone["y"])
    target = st.session_state.target

    new = compute_next(pos, target)

    st.session_state.drone["x"], st.session_state.drone["y"] = new
    st.session_state.path.append(new)

    update_landmarks(new)

# -----------------------------
# MAP
# -----------------------------
def render():
    fig = go.Figure()

    # Roads
    for i in range(0,100,10):
        fig.add_shape(type="line", x0=i,y0=0,x1=i,y1=100,line=dict(color="gray",width=1))
        fig.add_shape(type="line", x0=0,y0=i,x1=100,y1=i,line=dict(color="gray",width=1))

    # City objects with labels
    for obj in st.session_state.city:
        label = f"{icon(obj['type'])}<br>{obj['type']}<br>({obj['x']},{obj['y']})"
        fig.add_annotation(
            x=obj["x"], y=obj["y"],
            text=label,
            showarrow=False,
            font=dict(size=12)
        )

    # Hazards
    for h in st.session_state.hazards:
        fig.add_shape(
            type="circle",
            x0=h["x"]-3,y0=h["y"]-3,
            x1=h["x"]+3,y1=h["y"]+3,
            line_color="red"
        )

    # Path
    if len(st.session_state.path)>1:
        x,y=zip(*st.session_state.path)
        fig.add_trace(go.Scatter(
            x=x,y=y,
            mode="lines+markers",
            name="Trajectory"
        ))

    # Drone (LABELED)
    fig.add_annotation(
        x=st.session_state.drone["x"],
        y=st.session_state.drone["y"],
        text="🚁<br>H.A.W.K Drone",
        showarrow=False,
        font=dict(size=14)
    )

    # Target
    if st.session_state.target:
        fig.add_annotation(
            x=st.session_state.target[0],
            y=st.session_state.target[1],
            text="🎯 Target",
            showarrow=False,
            font=dict(size=14)
        )

    fig.update_layout(template="plotly_dark",height=600)
    return fig

# -----------------------------
# UI
# -----------------------------
st.set_page_config(layout="wide")
left,right = st.columns([3,1])

with left:
    st.subheader("🌆 Intelligent City Digital Twin")
    st.plotly_chart(render(), use_container_width=True)

    st.subheader("🗺️ Landmark Memory")
    df = pd.DataFrame(st.session_state.landmarks)
    st.dataframe(df, use_container_width=True)

with right:
    st.subheader("🧠 Command Center")

    cmd = st.text_input("Command","Go to hospital")

    if st.button("Execute Mission"):
        target_obj = parse(cmd)
        if target_obj:
            st.session_state.target = (target_obj["x"],target_obj["y"])
            st.session_state.running = True
            log(f"🚀 Navigating to {target_obj['type']}")
        else:
            log("❌ No valid target")

    if st.button("Pause"):
        st.session_state.running=False

    if st.button("Reset System"):
        st.session_state.clear()
        st.rerun()

    st.subheader("🚨 Hazard Injection")

    hx = st.slider("X",0,100,50)
    hy = st.slider("Y",0,100,50)

    if st.button("Add Hazard"):
        st.session_state.hazards.append({"x":hx,"y":hy})
        st.session_state.metrics["hazards"]+=1
        log(f"🚨 Hazard at ({hx},{hy})")

    st.subheader("📊 Metrics")
    st.metric("Hazards",st.session_state.metrics["hazards"])
    st.metric("Avoided",st.session_state.metrics["avoided"])
    st.metric("Near",st.session_state.metrics["near"])

    st.subheader("📡 Thought Trace")
    st.text_area("", "\n".join(st.session_state.logs), height=300)

# -----------------------------
# LOOP
# -----------------------------
if st.session_state.running and st.session_state.target:
    current=(st.session_state.drone["x"],st.session_state.drone["y"])

    if dist(current,st.session_state.target)<2:
        st.session_state.running=False
        log("✅ Target reached")
        st.balloons()
        st.rerun()
    else:
        update()
        time.sleep(0.08)
        st.rerun()
