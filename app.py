import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import time
import pandas as pd
import difflib
import re

# -----------------------------
# INIT
# -----------------------------
def init():
    st.session_state.drone = {"x": 10, "y": 10}
    st.session_state.path = [(10,10)]
    st.session_state.logs = []
    st.session_state.running = False
    st.session_state.target = None
    st.session_state.search_mode = False
    st.session_state.landmarks = []
    st.session_state.hazards = []
    st.session_state.metrics = {"hazards":0,"avoided":0,"near":0}

# -----------------------------
# SAFE CITY GENERATION
# -----------------------------
def generate_city():
    objs=[]

    def safe_add(x,y,t):
        for o in objs:
            if np.linalg.norm(np.array([x,y])-np.array([o["x"],o["y"]])) < 6:
                return False
        objs.append({"x":x,"y":y,"type":t})
        return True

    # homes + gardens
    for _ in range(8):
        x,y=random.randint(10,90),random.randint(10,90)
        if safe_add(x,y,"home"):
            safe_add(x+3,y+3,"garden")

    # hotels + pools
    for _ in range(5):
        x,y=random.randint(10,90),random.randint(10,90)
        if safe_add(x,y,"hotel"):
            safe_add(x+4,y,"pool")

    # trees (avoid overlap)
    for _ in range(12):
        safe_add(random.randint(5,95),random.randint(5,95),"tree")

    # cars (on roads approx)
    for _ in range(12):
        safe_add(random.randint(5,95),random.randint(5,95),"car")

    # dogs near structures
    for _ in range(10):
        safe_add(random.randint(5,95),random.randint(5,95),"dog")

    return objs

if "init" not in st.session_state:
    st.session_state.init=True
    st.session_state.city=generate_city()
    init()

# -----------------------------
# LOG
# -----------------------------
def log(x):
    st.session_state.logs.insert(0,x)

# -----------------------------
# DISTANCE
# -----------------------------
def dist(a,b):
    return np.linalg.norm(np.array(a)-np.array(b))

# -----------------------------
# FUZZY NLP
# -----------------------------
def match_word(word):
    types=list(set([o["type"] for o in st.session_state.city]))
    match=difflib.get_close_matches(word,types,n=1,cutoff=0.6)
    return match[0] if match else None

# -----------------------------
# NLP PARSER (WORKING)
# -----------------------------
def parse(cmd):
    cmd=cmd.lower()
    log(f"🧠 Parsing: {cmd}")

    words=cmd.split()

    target=None
    landmark=None
    distance_limit=None

    # detect numbers (distance)
    m=re.search(r'within (\d+)',cmd)
    if m:
        distance_limit=int(m.group(1))
        log(f"📏 Distance constraint: {distance_limit}")

    # fuzzy matching
    matched=[]
    for w in words:
        mw=match_word(w)
        if mw:
            matched.append(mw)

    if not matched:
        log("❌ Invalid instruction")
        return None

    target=matched[0]
    if len(matched)>1:
        landmark=matched[1]

    log(f"🎯 Target: {target}")
    if landmark:
        log(f"📍 Landmark: {landmark}")

    drone_pos=(st.session_state.drone["x"],st.session_state.drone["y"])
    objs=[o for o in st.session_state.city if o["type"]==target]

    # landmark constraint
    if landmark:
        land_objs=[o for o in st.session_state.city if o["type"]==landmark]
        valid=[]
        for l in land_objs:
            for o in objs:
                if dist((l["x"],l["y"]),(o["x"],o["y"]))<20:
                    valid.append(o)

        if not valid:
            log(f"❌ No {target} near {landmark}")
            return "search"

        objs=valid

    # distance constraint
    if distance_limit:
        objs=[o for o in objs if dist(drone_pos,(o["x"],o["y"]))<=distance_limit]
        if not objs:
            log("❌ No object within range")
            return None

    # choose nearest
    chosen=min(objs,key=lambda o:dist(drone_pos,(o["x"],o["y"])))
    log(f"✅ Selected {chosen['type']} at ({chosen['x']},{chosen['y']})")

    return chosen

# -----------------------------
# NAVIGATION (AVOIDANCE)
# -----------------------------
def next_step(pos,target):
    pos=np.array(pos)
    target=np.array(target)

    direction=target-pos
    direction=direction/(np.linalg.norm(direction)+1e-6)

    # avoid buildings + trees
    for o in st.session_state.city:
        if o["type"] in ["home","hotel","tree"]:
            p=np.array([o["x"],o["y"]])
            d=dist(pos,p)
            if d<8:
                rep=(pos-p)/(d+1e-6)
                direction+=rep*2

    # avoid hazards
    for h in st.session_state.hazards:
        p=np.array([h["x"],h["y"]])
        d=dist(pos,p)
        if d<8:
            rep=(pos-p)/(d+1e-6)
            direction+=rep*3
            st.session_state.metrics["avoided"]+=1

    direction=direction/(np.linalg.norm(direction)+1e-6)
    return tuple(pos+direction*1.5)

# -----------------------------
# UPDATE
# -----------------------------
def update():
    pos=(st.session_state.drone["x"],st.session_state.drone["y"])

    if st.session_state.search_mode:
        new=(pos[0]+random.uniform(-3,3),pos[1]+random.uniform(-3,3))
    else:
        new=next_step(pos,st.session_state.target)

    st.session_state.drone["x"],st.session_state.drone["y"]=new
    st.session_state.path.append(new)

# -----------------------------
# MAP
# -----------------------------
def render():
    fig=go.Figure()

    # roads (background)
    for i in range(0,101,20):
        fig.add_shape(type="rect",x0=i,y0=0,x1=i+6,y1=100,fillcolor="#222",layer="below")
        fig.add_shape(type="rect",x0=0,y0=i,x1=100,y1=i+6,fillcolor="#222",layer="below")

    # cursor coordinates
    fig.add_trace(go.Scatter(x=[0,100],y=[0,100],mode="markers",marker=dict(opacity=0),hoverinfo="x+y"))

    # objects
    for o in st.session_state.city:
        fig.add_trace(go.Scatter(
            x=[o["x"]],y=[o["y"]],
            mode="text",
            text=[o["type"][0].upper()],
            hovertext=f"{o['type']} ({o['x']},{o['y']})",
            showlegend=False
        ))

    # hazards
    for h in st.session_state.hazards:
        fig.add_trace(go.Scatter(x=[h["x"]],y=[h["y"]],mode="text",text=[h["type"]]))

    # path
    if len(st.session_state.path)>1:
        x,y=zip(*st.session_state.path)
        fig.add_trace(go.Scatter(x=x,y=y,mode="lines"))

    # drone
    fig.add_trace(go.Scatter(x=[st.session_state.drone["x"]],y=[st.session_state.drone["y"]],mode="text",text=["🚁"]))

    # target circle
    if st.session_state.target:
        x,y=st.session_state.target
        fig.add_shape(type="circle",x0=x-5,y0=y-5,x1=x+5,y1=y+5,line_color="yellow")

    fig.update_layout(template="plotly_dark",height=600)
    return fig

# -----------------------------
# UI
# -----------------------------
st.set_page_config(layout="wide")
left,right=st.columns([3,1])

with left:
    st.plotly_chart(render(),use_container_width=True)
    st.dataframe(pd.DataFrame(st.session_state.landmarks))

with right:
    cmd=st.text_input("Command","go to dog near pool")

    if st.button("Execute"):
        res=parse(cmd)

        if res=="search":
            st.session_state.search_mode=True
            st.session_state.running=True
            log("🔍 Searching map...")
        elif res:
            st.session_state.target=(res["x"],res["y"])
            st.session_state.running=True
            st.session_state.search_mode=False
        else:
            log("❌ Invalid instruction")

    hx=st.slider("X",0,100,50)
    hy=st.slider("Y",0,100,50)
    htype=st.selectbox("Obstacle",["🐦","🎈"])

    if st.button("Add Obstacle"):
        st.session_state.hazards.append({"x":hx,"y":hy,"type":htype})
        st.session_state.metrics["hazards"]+=1

    if st.session_state.hazards:
        opts=[f"{h['type']} ({h['x']},{h['y']})" for h in st.session_state.hazards]
        sel=st.selectbox("Remove obstacle",opts)
        if st.button("Remove"):
            st.session_state.hazards.pop(opts.index(sel))

    st.metric("Hazards",st.session_state.metrics["hazards"])
    st.metric("Avoided",st.session_state.metrics["avoided"])

    st.text_area("Logs","\n".join(st.session_state.logs),height=300)

# -----------------------------
# LOOP
# -----------------------------
if st.session_state.running:
    pos=(st.session_state.drone["x"],st.session_state.drone["y"])

    if st.session_state.target and dist(pos,st.session_state.target)<2:
        st.session_state.running=False
        log("✅ Instruction executed")
        st.rerun()

    update()
    time.sleep(0.08)
    st.rerun()
