import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import time

# -----------------------------
# INITIAL STATE
# -----------------------------
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.drone = {"x": 10, "y": 10}
    st.session_state.target = (90, 90)
    st.session_state.path = [(10, 10)]
    st.session_state.hazards = []
    st.session_state.logs = []
    st.session_state.running = False

    st.session_state.metrics = {
        "hazards": 0,
        "avoided": 0,
        "near": 0
    }

# -----------------------------
# LOGGER
# -----------------------------
def log(msg):
    t = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{t}] {msg}")

# -----------------------------
# DISTANCE
# -----------------------------
def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# -----------------------------
# REAL-TIME AVOIDANCE ENGINE
# -----------------------------
def compute_next_step(pos, target, hazards):
    x, y = pos

    dx = target[0] - x
    dy = target[1] - y

    step_x = np.sign(dx)
    step_y = np.sign(dy)

    next_x = x + step_x
    next_y = y + step_y

    for h in hazards:
        d = dist((next_x, next_y), (h["x"], h["y"]))

        if d < 6:
            st.session_state.metrics["near"] += 1
            log("⚠️ Hazard proximity detected")

        if d < 4:
            st.session_state.metrics["avoided"] += 1
            log("🚧 Avoidance maneuver triggered")

            next_x += random.choice([-2, 2])
            next_y += random.choice([-2, 2])

    return (next_x, next_y)

# -----------------------------
# UPDATE DRONE
# -----------------------------
def update_drone():
    pos = (st.session_state.drone["x"], st.session_state.drone["y"])
    target = st.session_state.target

    new_pos = compute_next_step(pos, target, st.session_state.hazards)

    st.session_state.drone["x"], st.session_state.drone["y"] = new_pos
    st.session_state.path.append(new_pos)

# -----------------------------
# DIGITAL TWIN MAP
# -----------------------------
def render_map():
    fig = go.Figure()

    # Path
    if len(st.session_state.path) > 1:
        x, y = zip(*st.session_state.path)
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name="AI Path"
        ))

    # Target
    fig.add_trace(go.Scatter(
        x=[st.session_state.target[0]],
        y=[st.session_state.target[1]],
        mode='markers',
        marker=dict(size=12, symbol="star"),
        name="Target"
    ))

    # Drone
    fig.add_trace(go.Scatter(
        x=[st.session_state.drone["x"]],
        y=[st.session_state.drone["y"]],
        mode='markers',
        marker=dict(size=14),
        name="Drone"
    ))

    # Hazards
    if st.session_state.hazards:
        hx = [h["x"] for h in st.session_state.hazards]
        hy = [h["y"] for h in st.session_state.hazards]

        fig.add_trace(go.Scatter(
            x=hx, y=hy,
            mode='markers',
            marker=dict(size=12, symbol="x"),
            name="Hazards"
        ))

    fig.update_layout(
        template="plotly_dark",
        height=600,
        margin=dict(l=0, r=0, t=30, b=0)
    )

    return fig

# -----------------------------
# UI
# -----------------------------
st.set_page_config(layout="wide")

left, right = st.columns([3, 1])

# -----------------------------
# LEFT: MAP
# -----------------------------
with left:
    st.subheader("🌍 Digital Twin Environment")
    st.plotly_chart(render_map(), use_container_width=True)

# -----------------------------
# RIGHT: CONTROL PANEL
# -----------------------------
with right:
    st.subheader("🧠 Mission Control")

    col1, col2 = st.columns(2)

    if col1.button("▶ Start"):
        st.session_state.running = True
        log("Mission Started")

    if col2.button("⏸ Pause"):
        st.session_state.running = False
        log("Mission Paused")

    if st.button("🔄 Reset"):
        st.session_state.clear()
        st.rerun()

    st.subheader("🚨 Hazard Injection")

    hx = st.slider("X Coordinate", 0, 100, 50)
    hy = st.slider("Y Coordinate", 0, 100, 50)

    if st.button("Inject Hazard"):
        st.session_state.hazards.append({"x": hx, "y": hy})
        st.session_state.metrics["hazards"] += 1
        log(f"🚨 Hazard injected at ({hx}, {hy})")

    st.subheader("📊 Metrics")

    st.metric("Total Hazards", st.session_state.metrics["hazards"])
    st.metric("Avoided", st.session_state.metrics["avoided"])
    st.metric("Near Collisions", st.session_state.metrics["near"])

    st.subheader("📡 Thought Trace")

    st.text_area("", "\n".join(st.session_state.logs), height=300)

# -----------------------------
# SMOOTH MOVEMENT LOOP (UPDATED)
# -----------------------------
if st.session_state.running:
    current_pos = (st.session_state.drone["x"], st.session_state.drone["y"])

    if dist(current_pos, st.session_state.target) < 2:
        st.session_state.running = False
        log("✅ Target Reached!")
        st.balloons()
        st.rerun()
    else:
        update_drone()
        time.sleep(0.08)  # smoother + safer speed
        st.rerun()
