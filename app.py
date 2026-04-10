import streamlit as st 
import plotly.graph_objects as go
import numpy as np
import time
import random
from streamlit_plotly_events import plotly_events

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
# SMART STEP (REAL-TIME AVOIDANCE)
# -----------------------------
def compute_next_step(pos, target, hazards):
    x, y = pos

    dx = target[0] - x
    dy = target[1] - y

    step_x = np.sign(dx)
    step_y = np.sign(dy)

    next_x = x + step_x
    next_y = y + step_y

    avoided = False

    for h in hazards:
        d = dist((next_x, next_y), (h["x"], h["y"]))

        # Near collision
        if d < 6:
            st.session_state.metrics["near"] += 1
            log("⚠️ Hazard proximity detected")

        # Avoidance trigger
        if d < 4:
            avoided = True
            st.session_state.metrics["avoided"] += 1
            log("🚧 Avoidance maneuver activated")

            next_x += random.choice([-2, 2])
            next_y += random.choice([-2, 2])

    return (next_x, next_y), avoided

# -----------------------------
# UPDATE DRONE (REAL-TIME)
# -----------------------------
def update_drone():
    pos = (st.session_state.drone["x"], st.session_state.drone["y"])
    target = st.session_state.target

    new_pos, _ = compute_next_step(pos, target, st.session_state.hazards)

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
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name="Path"))

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
        height=650,
        clickmode="event+select"
    )

    return fig

# -----------------------------
# UI
# -----------------------------
st.set_page_config(layout="wide")

left, right = st.columns([3, 1])

# -----------------------------
# MAP + INJECTION
# -----------------------------
with left:
    st.subheader("🌍 Digital Twin")

    fig = render_map()
    selected = plotly_events(fig)

    if selected:
        px = int(selected[0]["x"])
        py = int(selected[0]["y"])

        st.session_state.hazards.append({"x": px, "y": py})
        st.session_state.metrics["hazards"] += 1

        log(f"🚨 Hazard injected at ({px}, {py})")

# -----------------------------
# CONTROL PANEL
# -----------------------------
with right:
    st.subheader("🧠 Mission Control")

    if st.button("Start"):
        log("Mission Started")

    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()

    st.subheader("📊 Metrics")

    st.metric("Total Hazards", st.session_state.metrics["hazards"])
    st.metric("Avoided", st.session_state.metrics["avoided"])
    st.metric("Near Collisions", st.session_state.metrics["near"])

    st.subheader("📡 Thought Trace")
    st.text_area("", "\n".join(st.session_state.logs), height=350)

# -----------------------------
# MAIN LOOP
# -----------------------------
update_drone()
time.sleep(0.1)
st.rerun()
