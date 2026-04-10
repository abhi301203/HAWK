import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import time
import pandas as pd
import re

# -----------------------------
# INIT
# -----------------------------
def init_state():
    st.session_state.drone = {"x": 10, "y": 10}
    st.session_state.path = [(10, 10)]
    st.session_state.hazards = []
    st.session_state.logs = []
    st.session_state.running = False
    st.session_state.target = None
    st.session_state.pending_targets = []
    st.session_state.awaiting_selection = False

    st.session_state.metrics = {
        "hazards": 0,
        "avoided": 0,
        "near": 0
    }

    st.session_state.landmarks = []

if "init" not in st.session_state:
    st.session_state.init = True

    st.session_state.city = []
    types = [
        "home","hospital","school","church","hotel",
        "tree","garden","pool","car","truck","human","dog"
    ]

    for _ in range(60):
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
        "tree":"🌳","car":"🚗","truck":"🚛",
        "human":"🧍","dog":"🐕"
    }.get(t,"❓")

# -----------------------------
# LOGGER
# -----------------------------
def log(msg):
    st.session_state.logs.insert(0, msg)

# -----------------------------
# DISTANCE
# -----------------------------
def dist(a,b):
    return np.linalg.norm(np.array(a)-np.array(b))

# -----------------------------
# NLP + SMART SELECTION
# -----------------------------
def parse_command(cmd):
    cmd = cmd.lower()
    log(f"🧠 Processing: {cmd}")

    tokens = cmd.split()

    matches = []
    for t in tokens:
        for obj in st.session_state.city:
            if t == obj["type"]:
                matches.append(obj)

    if not matches:
        log("❌ No objects found")
        return None

    drone_pos = (st.session_state.drone["x"], st.session_state.drone["y"])

    # NEAR LOGIC
    if "near" in cmd:
        best = min(matches, key=lambda o: dist(drone_pos, (o["x"],o["y"])))
        log("🎯 Selecting nearest object")
        return best

    # WITHIN DISTANCE
    m = re.search(r'within (\d+)', cmd)
    if m:
        limit = int(m.group(1))
        filtered = [o for o in matches if dist(drone_pos,(o["x"],o["y"])) <= limit]

        if filtered:
            best = min(filtered, key=lambda o: dist(drone_pos,(o["x"],o["y"])))
            log(f"🎯 Selecting object within {limit} units")
            return best
        else:
            log("❌ No object within range")
            return None

    # MULTIPLE → ASK USER
    if len(matches) > 1:
        st.session_state.pending_targets = matches
        st.session_state.awaiting_selection = True
        log("🤖 Multiple targets detected. Awaiting user selection.")
        return None

    return matches[0]

# -----------------------------
# NAVIGATION
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

        if d < 5:
            st.session_state.metrics["avoided"] += 1
            log("🚧 Avoidance activated")

    direction = direction / (np.linalg.norm(direction)+1e-6)
    return tuple(pos + direction * 1.5)

def update():
    pos = (st.session_state.drone["x"], st.session_state.drone["y"])
    new = compute_next(pos, st.session_state.target)

    st.session_state.drone["x"], st.session_state.drone["y"] = new
    st.session_state.path.append(new)

    # Landmark memory
    for obj in st.session_state.city:
        if dist(new,(obj["x"],obj["y"])) < 3:
            entry = {
                "Type": obj["type"],
                "X": obj["x"],
                "Y": obj["y"],
                "Time": time.strftime("%H:%M:%S")
            }
            if entry not in st.session_state.landmarks:
                st.session_state.landmarks.append(entry)

# -----------------------------
# MAP
# -----------------------------
def render():
    fig = go.Figure()

    # Roads
    for i in range(0,101,10):
        fig.add_shape(type="line", x0=i,y0=0,x1=i,y1=100,line=dict(color="#444",width=4))
        fig.add_shape(type="line", x0=0,y0=i,x1=100,y1=i,line=dict(color="#444",width=4))

    # Cursor hover layer
    fig.add_trace(go.Scatter(x=[0,100],y=[0,100],
        mode="markers",marker=dict(opacity=0),hoverinfo="x+y"))

    # Objects
    for obj in st.session_state.city:
        if obj["type"] == "pool":
            fig.add_shape(type="rect",
                x0=obj["x"]-2,y0=obj["y"]-2,
                x1=obj["x"]+2,y1=obj["y"]+2,
                fillcolor="blue",line_color="blue")

        elif obj["type"] == "garden":
            fig.add_shape(type="rect",
                x0=obj["x"]-2,y0=obj["y"]-2,
                x1=obj["x"]+2,y1=obj["y"]+2,
                fillcolor="green",line_color="green")

        else:
            fig.add_trace(go.Scatter(
                x=[obj["x"]], y=[obj["y"]],
                mode="text",
                text=[icon(obj["type"])],
                textfont=dict(size=18),
                hovertext=f"{obj['type']} ({obj['x']},{obj['y']})",
                hoverinfo="text",
                showlegend=False
            ))

    # Path
    if len(st.session_state.path)>1:
        x,y=zip(*st.session_state.path)
        fig.add_trace(go.Scatter(x=x,y=y,mode="lines",name="Path"))

    # Drone
    fig.add_trace(go.Scatter(
        x=[st.session_state.drone["x"]],
        y=[st.session_state.drone["y"]],
        mode="text",
        text=["🚁"],
        textfont=dict(size=22),
        hovertext="H.A.W.K Drone",
        hoverinfo="text",
        showlegend=False
    ))

    # TARGET OUTLINE CIRCLE
    if st.session_state.target:
        x,y = st.session_state.target
        fig.add_shape(type="circle",
            x0=x-5,y0=y-5,x1=x+5,y1=y+5,
            line_color="yellow",line_width=3)

    fig.update_layout(template="plotly_dark",height=600)
    return fig

# -----------------------------
# UI
# -----------------------------
st.set_page_config(layout="wide")
left,right = st.columns([3,1])

with left:
    st.subheader("🌆 City Digital Twin")
    st.plotly_chart(render(), use_container_width=True)

    st.subheader("🗺️ Landmark Memory")
    st.dataframe(pd.DataFrame(st.session_state.landmarks), use_container_width=True)

with right:
    st.subheader("💬 AI Interaction")

    cmd = st.text_input("Command","go to car")

    if st.button("Send"):
        target_obj = parse_command(cmd)

        if target_obj:
            st.session_state.target = (target_obj["x"],target_obj["y"])
            st.session_state.running = True
            log(f"🚀 Navigating to {target_obj['type']}")

    if st.session_state.awaiting_selection:
        options = [
            f"{o['type']} ({o['x']},{o['y']})"
            for o in st.session_state.pending_targets
        ]

        choice = st.selectbox("Select Target", options)

        if st.button("Confirm"):
            idx = options.index(choice)
            selected = st.session_state.pending_targets[idx]

            st.session_state.target = (selected["x"],selected["y"])
            st.session_state.running = True
            st.session_state.awaiting_selection = False

    if st.button("Pause"):
        st.session_state.running=False

    if st.button("Reset"):
        st.session_state.clear()
        st.rerun()

    st.subheader("📊 Metrics")
    st.metric("Hazards",st.session_state.metrics["hazards"])
    st.metric("Avoided",st.session_state.metrics["avoided"])
    st.metric("Near",st.session_state.metrics["near"])

    st.subheader("📡 Logs")
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
