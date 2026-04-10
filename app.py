import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import time
import pandas as pd
import difflib
import re

# -----------------------------
# PAGE CONFIG (NASA STYLE)
# -----------------------------
st.set_page_config(layout="wide", page_title="H.A.W.K Mission Control")

# -----------------------------
# INIT
# -----------------------------
def init():
    st.session_state.drone = {"x": 10, "y": 10}
    st.session_state.path = [(10,10)]
    st.session_state.logs = ["🛰️ System Initialized"]
    st.session_state.running = False
    st.session_state.target = None
    st.session_state.search_mode = False
    st.session_state.landmarks = []
    st.session_state.hazards = []
    st.session_state.metrics = {"hazards":0,"avoided":0,"near":0}

# -----------------------------
# CITY GENERATION
# -----------------------------
def generate_city():
    objs=[]
    def safe_add(x,y,t):
        for o in objs:
            if np.linalg.norm(np.array([x,y])-np.array([o["x"],o["y"]])) < 6:
                return False
        objs.append({"x":x,"y":y,"type":t})
        return True

    for _ in range(8):
        x,y=random.randint(10,90),random.randint(10,90)
        if safe_add(x,y,"home"):
            safe_add(x+3,y+3,"garden")

    for _ in range(5):
        x,y=random.randint(10,90),random.randint(10,90)
        if safe_add(x,y,"hotel"):
            safe_add(x+4,y,"pool")

    for _ in range(10):
        safe_add(random.randint(5,95),random.randint(5,95),"tree")

    for _ in range(10):
        safe_add(random.randint(5,95),random.randint(5,95),"car")

    for _ in range(8):
        safe_add(random.randint(5,95),random.randint(5,95),"dog")

    return objs

if "init" not in st.session_state:
    st.session_state.init=True
    st.session_state.city=generate_city()
    init()

# -----------------------------
# ICONS
# -----------------------------
def icon_map(t):
    return {
        "home":"🏠","hotel":"🏨","tree":"🌳",
        "car":"🚗","dog":"🐕"
    }.get(t,"❓")

# -----------------------------
# LOG
# -----------------------------
def log(x):
    st.session_state.logs.insert(0,x)

# -----------------------------
# DIST
# -----------------------------
def dist(a,b):
    return np.linalg.norm(np.array(a)-np.array(b))

# -----------------------------
# NLP
# -----------------------------
def match_word(word):
    types=list(set([o["type"] for o in st.session_state.city]))
    m=difflib.get_close_matches(word,types,n=1,cutoff=0.6)
    return m[0] if m else None

def parse(cmd):
    cmd=cmd.lower()
    log(f"🧠 Processing: {cmd}")

    words=cmd.split()
    target=None
    landmark=None

    for w in words:
        m=match_word(w)
        if m:
            if not target:
                target=m
            else:
                landmark=m

    if not target:
        log("❌ Invalid instruction")
        return None

    objs=[o for o in st.session_state.city if o["type"]==target]

    if landmark:
        valid=[]
        for l in st.session_state.city:
            if l["type"]==landmark:
                for o in objs:
                    if dist((l["x"],l["y"]),(o["x"],o["y"]))<20:
                        valid.append(o)

        if not valid:
            log("❌ No object near landmark → searching")
            return "search"

        objs=valid

    drone=(st.session_state.drone["x"],st.session_state.drone["y"])
    return min(objs,key=lambda o:dist(drone,(o["x"],o["y"])))

# -----------------------------
# NAVIGATION
# -----------------------------
def next_step(pos,target):
    pos=np.array(pos)
    target=np.array(target)

    d=target-pos
    d=d/(np.linalg.norm(d)+1e-6)

    for o in st.session_state.city:
        if o["type"] in ["home","hotel","tree"]:
            p=np.array([o["x"],o["y"]])
            if dist(pos,p)<8:
                d+=(pos-p)/(dist(pos,p)+1e-6)*2

    for h in st.session_state.hazards:
        p=np.array([h["x"],h["y"]])
        if dist(pos,p)<8:
            d+=(pos-p)/(dist(pos,p)+1e-6)*3
            st.session_state.metrics["avoided"]+=1

    d=d/(np.linalg.norm(d)+1e-6)
    return tuple(pos+d*1.5)

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

    # ROADS
    for i in range(0,101,20):
        fig.add_shape(type="rect",x0=i,y0=0,x1=i+6,y1=100,fillcolor="#222",layer="below")
        fig.add_shape(type="rect",x0=0,y0=i,x1=100,y1=i+6,fillcolor="#222",layer="below")

    # CURSOR
    fig.add_trace(go.Scatter(x=[0,100],y=[0,100],mode="markers",marker=dict(opacity=0),hoverinfo="x+y"))

    # OBJECTS
    for o in st.session_state.city:
        if o["type"]=="pool":
            fig.add_shape(type="rect",x0=o["x"]-2,y0=o["y"]-2,x1=o["x"]+2,y1=o["y"]+2,fillcolor="blue")
        elif o["type"]=="garden":
            fig.add_shape(type="rect",x0=o["x"]-2,y0=o["y"]-2,x1=o["x"]+2,y1=o["y"]+2,fillcolor="green")
        else:
            fig.add_trace(go.Scatter(
                x=[o["x"]],y=[o["y"]],
                mode="text",
                text=[icon_map(o["type"])],
                textfont=dict(size=22),
                hovertext=f"{o['type']} ({o['x']},{o['y']})",
                showlegend=False
            ))

    # PATH
    if len(st.session_state.path)>1:
        x,y=zip(*st.session_state.path)
        fig.add_trace(go.Scatter(x=x,y=y,mode="lines",name="Path"))

    # DRONE
    fig.add_trace(go.Scatter(
        x=[st.session_state.drone["x"]],
        y=[st.session_state.drone["y"]],
        mode="text",
        text=["🚁"],
        textfont=dict(size=26),
        hovertext="H.A.W.K Drone"
    ))

    # TARGET
    if st.session_state.target:
        x,y=st.session_state.target
        fig.add_shape(type="circle",x0=x-6,y0=y-6,x1=x+6,y1=y+6,line_color="yellow",line_width=3)

    return fig

# -----------------------------
# UI LAYOUT (NASA STYLE)
# -----------------------------
col1,col2=st.columns([3,1])

with col1:
    st.subheader("🌍 Digital Twin")
    st.plotly_chart(render(),use_container_width=True)

with col2:
    st.subheader("🧠 AI Control")

    cmd=st.text_input("Command","go to dog near pool")

    if st.button("Execute"):
        res=parse(cmd)

        if res=="search":
            st.session_state.search_mode=True
            st.session_state.running=True
        elif res:
            st.session_state.target=(res["x"],res["y"])
            st.session_state.running=True
            st.session_state.search_mode=False

    st.subheader("🚨 Obstacles")
    hx=st.slider("X",0,100,50)
    hy=st.slider("Y",0,100,50)
    htype=st.selectbox("Type",["🐦","🎈"])

    if st.button("Add"):
        st.session_state.hazards.append({"x":hx,"y":hy,"type":htype})

    st.metric("Avoided",st.session_state.metrics["avoided"])

    st.subheader("📡 Logs")
    st.text_area("", "\n".join(st.session_state.logs), height=300)

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
