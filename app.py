import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import time
import difflib

st.set_page_config(layout="wide")

MAP_SIZE = 200

# -----------------------------
# INIT (RUN ONLY ONCE)
# -----------------------------
if "initialized" not in st.session_state:

    def create_city():
        objs = []

        def add(x, y, t):
            objs.append({"x": x, "y": y, "type": t})

        # Residential zone
        for i in range(20, 80, 15):
            for j in range(20, 80, 15):
                add(i, j, "home")
                add(i+4, j+4, "garden")

        # Education zone
        add(120, 40, "school")
        add(130, 50, "college")
        add(125, 45, "garden")

        # Mall + parking
        add(150, 120, "mall")
        for i in range(140, 170, 10):
            add(i, 110, "car")

        # Hotel + pool
        add(50, 140, "hotel")
        add(60, 140, "pool")

        # Church
        add(30, 150, "church")

        # Trees
        for _ in range(20):
            add(random.randint(10, 190), random.randint(10, 190), "tree")

        # Dogs
        for _ in range(10):
            add(random.randint(10, 190), random.randint(10, 190), "dog")

        return objs

    st.session_state.city = create_city()
    st.session_state.drone = {"x": 10, "y": 10}
    st.session_state.path = [(10, 10)]
    st.session_state.logs = ["🛰️ System Initialized"]
    st.session_state.running = False
    st.session_state.target = None
    st.session_state.hazards = []
    st.session_state.metrics = {"avoided": 0}
    st.session_state.landmarks = []

    st.session_state.initialized = True

# -----------------------------
# UTILS
# -----------------------------
def log(msg):
    st.session_state.logs.insert(0, msg)

def dist(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def match(word):
    types = list(set([o["type"] for o in st.session_state.city]))
    m = difflib.get_close_matches(word, types, n=1, cutoff=0.6)
    return m[0] if m else None

# -----------------------------
# NLP PARSER
# -----------------------------
def parse(cmd):
    cmd = cmd.lower()
    log(f"🧠 Command: {cmd}")

    words = cmd.split()
    target = None
    landmark = None

    for w in words:
        m = match(w)
        if m:
            if not target:
                target = m
            else:
                landmark = m

    if not target:
        log("❌ Invalid instruction")
        return None

    objs = [o for o in st.session_state.city if o["type"] == target]

    if landmark:
        objs = [o for o in objs if any(
            dist((o["x"], o["y"]), (l["x"], l["y"])) < 25
            for l in st.session_state.city if l["type"] == landmark
        )]

        if not objs:
            log(f"❌ No {target} near {landmark}")
            return None

    drone = (st.session_state.drone["x"], st.session_state.drone["y"])
    chosen = min(objs, key=lambda o: dist(drone, (o["x"], o["y"])))

    log(f"🎯 Selected {chosen['type']} at ({chosen['x']},{chosen['y']})")
    return chosen

# -----------------------------
# NAVIGATION
# -----------------------------
def next_step(pos, target):
    pos = np.array(pos)
    target = np.array(target)

    d = target - pos
    d = d / (np.linalg.norm(d) + 1e-6)

    for o in st.session_state.city:
        if o["type"] in ["home", "hotel", "tree", "mall", "school"]:
            p = np.array([o["x"], o["y"]])
            if dist(pos, p) < 10:
                d += (pos - p) / (dist(pos, p) + 1e-6) * 2

    for h in st.session_state.hazards:
        p = np.array([h["x"], h["y"]])
        if dist(pos, p) < 10:
            d += (pos - p) / (dist(pos, p) + 1e-6) * 3
            st.session_state.metrics["avoided"] += 1

    d = d / (np.linalg.norm(d) + 1e-6)
    return tuple(pos + d * 2)

# -----------------------------
# UPDATE
# -----------------------------
def update():
    pos = (st.session_state.drone["x"], st.session_state.drone["y"])
    new = next_step(pos, st.session_state.target)

    st.session_state.drone["x"], st.session_state.drone["y"] = new
    st.session_state.path.append(new)

# -----------------------------
# MAP
# -----------------------------
def render():
    fig = go.Figure()

    # roads
    for i in range(0, MAP_SIZE, 40):
        fig.add_shape(type="rect", x0=i, y0=0, x1=i+10, y1=MAP_SIZE, fillcolor="#222", layer="below")
        fig.add_shape(type="rect", x0=0, y0=i, x1=MAP_SIZE, y1=i+10, fillcolor="#222", layer="below")

    # cursor
    fig.add_trace(go.Scatter(
        x=[0, MAP_SIZE], y=[0, MAP_SIZE],
        mode="markers", marker=dict(opacity=0),
        hoverinfo="x+y"
    ))

    # objects
    for o in st.session_state.city:
        if o["type"] == "pool":
            fig.add_shape(type="rect", x0=o["x"]-3, y0=o["y"]-3,
                          x1=o["x"]+3, y1=o["y"]+3, fillcolor="blue")
        elif o["type"] == "garden":
            fig.add_shape(type="rect", x0=o["x"]-3, y0=o["y"]-3,
                          x1=o["x"]+3, y1=o["y"]+3, fillcolor="green")
        else:
            fig.add_trace(go.Scatter(
                x=[o["x"]], y=[o["y"]],
                mode="text",
                text=[o["type"][0].upper()],
                hovertext=f"{o['type']} ({o['x']},{o['y']})",
                showlegend=False
            ))

    # drone
    fig.add_trace(go.Scatter(
        x=[st.session_state.drone["x"]],
        y=[st.session_state.drone["y"]],
        mode="text",
        text=["🚁"],
        textfont=dict(size=24)
    ))

    # path
    if len(st.session_state.path) > 1:
        x, y = zip(*st.session_state.path)
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines"))

    # target
    if st.session_state.target:
        x, y = st.session_state.target
        fig.add_shape(type="circle", x0=x-6, y0=y-6, x1=x+6, y1=y+6, line_color="yellow")

    fig.update_layout(template="plotly_dark", height=700)
    return fig

# -----------------------------
# UI
# -----------------------------
left, right = st.columns([3, 1])

with left:
    st.plotly_chart(render(), use_container_width=True)

with right:
    cmd = st.text_input("Command", "go to dog near pool")

    if st.button("Execute"):
        res = parse(cmd)
        if res:
            st.session_state.target = (res["x"], res["y"])
            st.session_state.running = True

    # hazards
    hx = st.slider("X", 0, MAP_SIZE, 50)
    hy = st.slider("Y", 0, MAP_SIZE, 50)

    if st.button("Add Hazard"):
        st.session_state.hazards.append({"x": hx, "y": hy})

    st.metric("Avoided", st.session_state.metrics["avoided"])

    st.text_area("Logs", "\n".join(st.session_state.logs), height=300)

# -----------------------------
# LOOP
# -----------------------------
if st.session_state.running:
    pos = (st.session_state.drone["x"], st.session_state.drone["y"])

    if st.session_state.target and dist(pos, st.session_state.target) < 2:
        st.session_state.running = False
        log("✅ Instruction executed")
        st.rerun()

    update()
    time.sleep(0.08)
    st.rerun()
