import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
import random

# -----------------------------
# SYSTEM STATE INITIALIZATION
# -----------------------------
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.drone = {"x": 10, "y": 10}
    st.session_state.path = [(10, 10)]
    st.session_state.ghost_path = [(10, 10)]
    st.session_state.obstacles = []
    st.session_state.logs = []
    st.session_state.target = (80, 80)

# -----------------------------
# LOGGER (THOUGHT TRACE)
# -----------------------------
def log(msg):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{timestamp}] {msg}")

# -----------------------------
# LATENCY SIMULATOR
# -----------------------------
def simulate_latency(stage):
    delay = random.uniform(0.2, 0.8)
    log(f"{stage}...")
    time.sleep(delay)
    log(f"{stage} completed in {round(delay,2)}s")

# -----------------------------
# DISTANCE FUNCTION
# -----------------------------
def distance(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# -----------------------------
# PATH PLANNER (INTELLIGENT)
# -----------------------------
def plan_path(start, target, obstacles):
    simulate_latency("Neural Path Planning")

    path = []
    x, y = start

    for _ in range(200):
        dx = target[0] - x
        dy = target[1] - y

        step_x = np.sign(dx)
        step_y = np.sign(dy)

        new_x = x + step_x
        new_y = y + step_y

        # Obstacle avoidance
        for obs in obstacles:
            if distance((new_x, new_y), (obs["x"], obs["y"])) < 5:
                log("⚠️ Obstacle detected → Adjusting trajectory")
                new_x += random.choice([-2, 2])
                new_y += random.choice([-2, 2])

        x, y = new_x, new_y
        path.append((x, y))

        if distance((x, y), target) < 2:
            break

    return path

# -----------------------------
# DRONE MOVEMENT ENGINE
# -----------------------------
def update_drone():
    if len(st.session_state.path) > 1:
        next_pos = st.session_state.path[1]
        st.session_state.drone["x"], st.session_state.drone["y"] = next_pos
        st.session_state.path.pop(0)

# -----------------------------
# DIGITAL TWIN RENDER
# -----------------------------
def render_map():
    fig = go.Figure()

    # AI Path
    if len(st.session_state.path) > 1:
        x, y = zip(*st.session_state.path)
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name="AI Path"))

    # Ghost Path (baseline)
    gx = [p[0] for p in st.session_state.ghost_path]
    gy = [p[1] for p in st.session_state.ghost_path]
    fig.add_trace(go.Scatter(
        x=gx, y=gy,
        mode='lines',
        name="Baseline",
        line=dict(dash='dash')
    ))

    # Drone
    fig.add_trace(go.Scatter(
        x=[st.session_state.drone["x"]],
        y=[st.session_state.drone["y"]],
        mode='markers',
        marker=dict(size=14),
        name="Drone"
    ))

    # Obstacles
    if st.session_state.obstacles:
        ox = [o["x"] for o in st.session_state.obstacles]
        oy = [o["y"] for o in st.session_state.obstacles]

        fig.add_trace(go.Scatter(
            x=ox, y=oy,
            mode='markers',
            marker=dict(size=10, symbol='x'),
            name="Obstacles"
        ))

    fig.update_layout(
        template="plotly_dark",
        height=600,
        clickmode='event+select'
    )

    return fig

# -----------------------------
# UI LAYOUT
# -----------------------------
st.set_page_config(layout="wide")

col1, col2 = st.columns([3, 1])

# -----------------------------
# LEFT: DIGITAL TWIN
# -----------------------------
with col1:
    st.subheader("🌍 Digital Twin Environment")

    fig = render_map()
    selected = st.plotly_chart(fig, use_container_width=True)

    # CLICK → INJECT OBSTACLE
    if selected and "points" in selected:
        point = selected["points"][0]
        x, y = int(point["x"]), int(point["y"])

        st.session_state.obstacles.append({"x": x, "y": y})
        log(f"🚨 Hazard injected at ({x}, {y})")

        # Trigger replanning
        st.session_state.path = plan_path(
            (st.session_state.drone["x"], st.session_state.drone["y"]),
            st.session_state.target,
            st.session_state.obstacles
        )

# -----------------------------
# RIGHT: CONTROL PANEL
# -----------------------------
with col2:
    st.subheader("🧠 Command HUD")

    if st.button("Start Mission"):
        log("Mission Started")
        st.session_state.path = plan_path(
            (st.session_state.drone["x"], st.session_state.drone["y"]),
            st.session_state.target,
            st.session_state.obstacles
        )

    if st.button("Reset"):
        st.session_state.drone = {"x": 10, "y": 10}
        st.session_state.path = [(10, 10)]
        st.session_state.obstacles = []
        st.session_state.logs = []
        log("System Reset")

    st.subheader("📡 Thought Trace")
    st.text_area("", "\n".join(st.session_state.logs), height=400)

# -----------------------------
# MAIN LOOP SIMULATION
# -----------------------------
update_drone()
time.sleep(0.1)
st.rerun()
