import plotly.graph_objects as go
import numpy as np

# Idea 4: Digital Twin Dataset
ENV_DATA = {
    "landmarks": [
        {"id": "HQ", "name": "BASE STATION", "pos": [5, 5], "icon": "🛰️"},
        {"id": "MED", "name": "HOSPITAL", "pos": [15, 45], "icon": "🏥"},
        {"id": "EDU", "name": "UNIVERSITY", "pos": [45, 40], "icon": "🏫"},
        {"id": "RES", "name": "RESIDENTIAL", "pos": [40, 10], "icon": "🏠"}
    ],
    "roads": [
        {"x": [0, 50], "y": [25, 25]}, {"x": [25, 25], "y": [0, 50]}
    ]
}

def build_mission_map(uav_pos, path_x, path_y, ghost_x, ghost_y, hazards_active=False):
    fig = go.Figure()
    
    # Render Infrastructure
    for road in ENV_DATA["roads"]:
        fig.add_trace(go.Scatter(x=road["x"], y=road["y"], mode='lines', 
                                 line=dict(color='#222', width=40), hoverinfo='skip'))

    # Idea 15: Ghost Trajectory (Red Dotted)
    if len(ghost_x) > 0:
        fig.add_trace(go.Scatter(x=ghost_x, y=ghost_y, mode='lines', 
                                 line=dict(color='#FF5252', width=1, dash='dot'), name="Standard Model"))

    # HAWK AI Trajectory (Green Solid)
    if len(path_x) > 0:
        fig.add_trace(go.Scatter(x=path_x, y=path_y, mode='lines', 
                                 line=dict(color='#00FF41', width=3), name="HAWK AI"))

    # Idea 10: Stress-Tester Hazards
    if hazards_active:
        fig.add_trace(go.Scatter(x=[20, 30], y=[30, 15], mode='text', text=["🚧", "🚧"], textfont=dict(size=30)))

    # Landmarks
    for lm in ENV_DATA["landmarks"]:
        fig.add_trace(go.Scatter(x=[lm["pos"][0]], y=[lm["pos"][1]], mode='text', text=[lm["icon"]],
                                 textfont=dict(size=28), name=lm["name"]))

    # UAV Agent (X)
    fig.add_trace(go.Scatter(x=[uav_pos[0]], y=[uav_pos[1]], mode='markers+text', text=["X"],
                             marker=dict(size=18, color="white", symbol="x-thin-open"), textfont=dict(color="white", size=15)))

    # Optimized Layout for Screen Fitting
    fig.update_layout(template="plotly_dark", xaxis=dict(range=[0, 50], visible=False), 
                      yaxis=dict(range=[0, 50], visible=False), height=500, # Reduced height for scroll-free view
                      margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
    return fig
