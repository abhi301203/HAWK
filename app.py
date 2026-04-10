import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import time

# -----------------------------
# INIT STATE
# -----------------------------
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.drone = {"x": 10, "y": 10}
    st.session_state.path = [(10, 10)]
    st.session_state.hazards = []
    st.session_state.logs = []
    st.session_state.running = False
    st.session_state.target = None

    # Semantic city map
    st.session_state.city = [
        {"x": 80, "y": 80, "type": "hospital"},
        {"x": 20, "y": 70, "type": "school"},
        {"x": 60, "y": 30, "type": "building"},
        {"x": 40, "y": 50, "type": "garden"},
        {"x": 70, "y": 20, "type": "car"},
    ]

    st.session_state.metrics = {
        "hazards": 0,
        "avoided": 0,
        "near": 0
    }

# -----------------------------
# ICONS
# -----------------------------
def get_icon(t):
    icons = {
        "hospital": "🏥",
        "school": "🏫",
        "building": "🏠",
        "garden": "🌿",
        "car": "🚗"
    }
    return icons.get(t, "❓")

# -----------------------------
# LOGGER
# -----------------------------
def log(msg):
    t = time.strftime("%H:%M:%S")
    st.session_state.logs.insert(0, f"[{t}] {msg}")

# -----------------------------
# NLP PARSER (SIMULATED)
# -----------------------------
def parse_command(cmd):
    log("🧠 NLP Processing Started")

    tokens = cmd.lower().split()
    log(f"Tokens: {tokens}")

    intent = "navigate" if "go" in tokens else "unknown"
    log(f"Intent: {intent}")

    target = None
    for word in tokens:
        for obj in st.session_state.city:
            if word == obj["type"]:
                target = obj
                log(f"Target identified: {word}")

    return intent, target

# -----------------------------
# DISTANCE
# -----------------------------
def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# -----------------------------
# MOVEMENT
# -----------------------------
def compute_next_step(pos, target, hazards):
    x, y = pos

    dx = target[0] - x
    dy = target[1] - y

    next_x = x + np.sign(dx)
    next_y = y + np.sign(dy)

    for h in hazards:
        d = dist((next_x, next_y), (h["x"], h["y"]))

        if d < 6:
            st.session_state.metrics["near"] += 1
            log("⚠️ Hazard nearby")

        if d < 4:
            st.session_state.metrics["avoided"] += 1
            log("🚧 Avoidance triggered")

            next_x += random.choice([-2, 2])
            next_y += random.choice([-2, 2])

    return (next_x, next_y)

def update_drone():
    pos = (st.session_state.drone["x"], st.session_state.drone["y"])
    target = st.session_state.target

    new_pos = compute_next_step(pos, target, st.session_state.hazards)

    st.session_state.drone["x"], st.session_state.drone["y"] = new_pos
    st.session_state.path.append(new_pos)

# -----------------------------
# MAP
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

    # City objects
    for obj in st.session_state.city:
        fig.add_annotation(
            x=obj["x"],
            y=obj["y"],
            text=get_icon(obj["type"]),
            showarrow=False,
            font=dict(size=20)
        )

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

    fig.update_layout(template="plotly_dark", height=600)
    return fig

# -----------------------------
# UI
# -----------------------------
st.set_page_config(layout="wide")

left, right = st.columns([3, 1])

# -----------------------------
# LEFT MAP
# -----------------------------
with left:
    st.subheader("🌆 Intelligent City Map")
    st.plotly_chart(render_map(), use_container_width=True)

# -----------------------------
# RIGHT PANEL
# -----------------------------
with right:
    st.subheader("🧠 Command Center")

    cmd = st.text_input("Enter Command", "Go to hospital")

    if st.button("Execute"):
        intent, target = parse_command(cmd)

        if target:
            st.session_state.target = (target["x"], target["y"])
            st.session_state.running = True
            log(f"📍 Navigating to {target['type']}")
        else:
            log("❌ No valid target found")

    if st.button("Pause"):
        st.session_state.running = False

    st.subheader("🚨 Hazard Injection")

    hx = st.slider("X", 0, 100, 50)
    hy = st.slider("Y", 0, 100, 50)

    if st.button("Inject Hazard"):
        st.session_state.hazards.append({"x": hx, "y": hy})
        st.session_state.metrics["hazards"] += 1
        log(f"🚨 Hazard at ({hx},{hy})")

    st.subheader("📊 Metrics")
    st.metric("Hazards", st.session_state.metrics["hazards"])
    st.metric("Avoided", st.session_state.metrics["avoided"])
    st.metric("Near", st.session_state.metrics["near"])

    st.subheader("📡 AI Thought Trace")
    st.text_area("", "\n".join(st.session_state.logs), height=300)

# -----------------------------
# LOOP
# -----------------------------
if st.session_state.running and st.session_state.target:
    current = (st.session_state.drone["x"], st.session_state.drone["y"])

    if dist(current, st.session_state.target) < 2:
        st.session_state.running = False
        log("✅ Target reached")
        st.balloons()
        st.rerun()
    else:
        update_drone()
        time.sleep(0.08)
        st.rerun()
