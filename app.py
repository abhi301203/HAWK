import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import time
import pandas as pd
import difflib
import re

st.set_page_config(layout="wide")

MAP_SIZE = 200

# -----------------------------
# INIT
# -----------------------------
def init():
    st.session_state.drone = {"x": 20, "y": 20}
    st.session_state.path = [(20,20)]
    st.session_state.logs = ["🛰️ System Ready"]
    st.session_state.running = False
    st.session_state.target = None
    st.session_state.search_mode = False
    st.session_state.hazards = []
    st.session_state.metrics = {"hazards":0,"avoided":0}

# -----------------------------
# CITY GENERATION (REALISTIC)
# -----------------------------
def generate_city():
    objs=[]

    def safe(x,y):
        for o in objs:
            if np.linalg.norm(np.array([x,y])-np.array([o["x"],o["y"]]))<8:
                return False
        return True

    def add(x,y,t):
        if safe(x,y):
            objs.append({"x":x,"y":y,"type":t})

    # neighborhoods
    for _ in range(10):
        x,y=random.randint(20,180),random.randint(20,180)
        add(x,y,"home")
        add(x+4,y+4,"garden")

    # schools/colleges cluster
    for _ in range(4):
        x,y=random.randint(30,170),random.randint(30,170)
        add(x,y,"school")
        add(x+5,y,"college")
        add(x+2,y+3,"garden")

    # malls + parking
    for _ in range(3):
        x,y=random.randint(30,170),random.randint(30,170)
        add(x,y,"mall")
        for _ in range(3):
            add(x+random.randint(-6,6),y+random.randint(-6,6),"car")

    # hotels + pool
    for _ in range(4):
        x,y=random.randint(30,170),random.randint(30,170)
        add(x,y,"hotel")
        add(x+5,y,"pool")

    # church
    for _ in range(3):
        add(random.randint(20,180),random.randint(20,180),"church")

    # trees
    for _ in range(20):
        add(random.randint(10,190),random.randint(10,190),"tree")

    # dogs
    for _ in range(12):
        add(random.randint(10,190),random.randint(10,190),"dog")

    return objs

if "init" not in st.session_state:
    st.session_state.city = generate_city()
    init()

# -----------------------------
# ICONS
# -----------------------------
def icon(t):
    return {
        "home":"🏠","hotel":"🏨","school":"🏫","college":"🎓",
        "church":"⛪","mall":"🏬","tree":"🌳",
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
def match(word):
    types=list(set([o["type"] for o in st.session_state.city]))
    m=difflib.get_close_matches(word,types,n=1,cutoff=0.6)
    return m[0] if m else None

def parse(cmd):
    cmd=cmd.lower()
    log(f"🧠 {cmd}")

    words=cmd.split()
    target=None
    landmark=None

    for w in words:
        m=match(w)
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
        objs=[o for o in objs if any(
            dist((o["x"],o["y"]),(l["x"],l["y"]))<20
            for l in st.session_state.city if l["type"]==landmark
        )]

        if not objs:
            log("❌ No match → searching")
            return "search"

    drone=(st.session_state.drone["x"],st.session_state.drone["y"])
    objs=sorted(objs,key=lambda o:dist(drone,(o["x"],o["y"])))

    if len(objs)>1:
        st.session_state.choices=objs[:5]
        return "choose"

    return objs[0]

# -----------------------------
# NAVIGATION
# -----------------------------
def next_step(pos,target):
    pos=np.array(pos)
    target=np.array(target)

    d=target-pos
    d=d/(np.linalg.norm(d)+1e-6)

    for o in st.session_state.city:
        if o["type"] in ["home","hotel","tree","mall","school"]:
            p=np.array([o["x"],o["y"]])
            if dist(pos,p)<10:
                d+=(pos-p)/(dist(pos,p)+1e-6)*2

    for h in st.session_state.hazards:
        p=np.array([h["x"],h["y"]])
        if dist(pos,p)<10:
            d+=(pos-p)/(dist(pos,p)+1e-6)*3
            st.session_state.metrics["avoided"]+=1

    d=d/(np.linalg.norm(d)+1e-6)
    return tuple(pos+d*2)

# -----------------------------
# UPDATE
# -----------------------------
def update():
    pos=(st.session_state.drone["x"],st.session_state.drone["y"])

    if st.session_state.search_mode:
        new=(pos[0]+random.uniform(-4,4),pos[1]+random.uniform(-4,4))
    else:
        new=next_step(pos,st.session_state.target)

    st.session_state.drone["x"],st.session_state.drone["y"]=new
    st.session_state.path.append(new)

# -----------------------------
# MAP
# -----------------------------
def render():
    fig=go.Figure()

    # roads
    for i in range(0,MAP_SIZE,40):
        fig.add_shape(type="rect",x0=i,y0=0,x1=i+8,y1=MAP_SIZE,fillcolor="#222",layer="below")
        fig.add_shape(type="rect",x0=0,y0=i,x1=MAP_SIZE,y1=i+8,fillcolor="#222",layer="below")

    # cursor
    fig.add_trace(go.Scatter(x=[0,MAP_SIZE],y=[0,MAP_SIZE],
        mode="markers",marker=dict(opacity=0),hoverinfo="x+y"))

    # objects
    for o in st.session_state.city:
        if o["type"]=="pool":
            fig.add_shape(type="rect",x0=o["x"]-3,y0=o["y"]-3,
                          x1=o["x"]+3,y1=o["y"]+3,fillcolor="blue")
        elif o["type"]=="garden":
            fig.add_shape(type="rect",x0=o["x"]-3,y0=o["y"]-3,
                          x1=o["x"]+3,y1=o["y"]+3,fillcolor="green")
        else:
            fig.add_trace(go.Scatter(
                x=[o["x"]],y=[o["y"]],
                mode="text",
                text=[icon(o["type"])],
                textfont=dict(size=18),
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
    fig.add_trace(go.Scatter(
        x=[st.session_state.drone["x"]],
        y=[st.session_state.drone["y"]],
        mode="text",
        text=["🚁"],
        textfont=dict(size=24)
    ))

    # target
    if st.session_state.target:
        x,y=st.session_state.target
        fig.add_shape(type="circle",x0=x-6,y0=y-6,x1=x+6,y1=y+6,line_color="yellow")

    fig.update_layout(template="plotly_dark",height=700)
    return fig

# -----------------------------
# UI
# -----------------------------
left,right=st.columns([3,1])

with left:
    st.plotly_chart(render(),use_container_width=True)

with right:
    st.subheader("🧠 AI Interface")

    cmd=st.text_input("Command","go to dog near pool")

    if st.button("Execute"):
        res=parse(cmd)

        if res=="search":
            st.session_state.search_mode=True
            st.session_state.running=True
        elif res=="choose":
            pass
        elif res:
            st.session_state.target=(res["x"],res["y"])
            st.session_state.running=True

    if "choices" in st.session_state:
        options=[f"{o['type']} ({o['x']},{o['y']})" for o in st.session_state.choices]
        sel=st.selectbox("Choose target",options)
        if st.button("Confirm"):
            idx=options.index(sel)
            o=st.session_state.choices[idx]
            st.session_state.target=(o["x"],o["y"])
            st.session_state.running=True

    st.subheader("🚨 Obstacles")

    hx=st.slider("X",0,MAP_SIZE,50)
    hy=st.slider("Y",0,MAP_SIZE,50)
    typ=st.selectbox("Type",["🐦","🎈"])

    if st.button("Add"):
        st.session_state.hazards.append({"x":hx,"y":hy,"type":typ})
        st.session_state.metrics["hazards"]+=1

    if st.session_state.hazards:
        opts=[f"{h['type']} ({h['x']},{h['y']})" for h in st.session_state.hazards]
        sel=st.selectbox("Remove",opts)
        if st.button("Delete"):
            st.session_state.hazards.pop(opts.index(sel))

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
