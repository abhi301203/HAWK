import plotly.graph_objects as go
import numpy as np

# Idea 4: Comprehensive City Infrastructure
CITY_DATA = {
    "zones": {
        "residential": {"x": [35, 48, 48, 35], "y": [2, 2, 15, 15], "color": "rgba(0, 255, 255, 0.1)"},
        "industrial": {"x": [2, 15, 15, 2], "y": [35, 35, 48, 48], "color": "rgba(255, 0, 0, 0.1)"}
    },
    "landmarks": [
        {"name": "BASE_STATION", "pos": [2, 2], "icon": "🛰️", "type": "HQ"},
        {"name": "HOSPITAL_ALPHA", "pos": [5, 45], "icon": "🏥", "type": "MEDICAL"},
        {"name": "SCHOOL_BETA", "pos": [35, 45], "icon": "🏫", "type": "EDU"},
        {"name": "HOME_SEC_8", "pos": [45, 5], "icon": "🏠", "type": "CIVIL"},
        {"name": "GOVT_W_HOUSE", "pos": [10, 40], "icon": "🏭", "type": "GOV"}
    ],
    "roads": [
        {"x": [0, 50], "y": [25, 25]}, {"x": [25, 25], "y": [0, 50]},
        {"x": [0, 50], "y": [5, 5]}, {"x": [5, 5], "y": [0, 50]}
    ]
}

def build_4d_environment(uav_pos, path_data, ghost_data, hazards, perception_range=8):
    fig = go.Figure()
    
    # Render City Zones
    for zone in CITY_DATA["zones"].values():
        fig.add_trace(go.Scatter(x=zone["x"], y=zone["y"], fill="toself", fillcolor=zone["color"], line=dict(width=0), hoverinfo='skip'))

    # Render Roads (Semantic Paths)
    for road in CITY_DATA["roads"]:
        fig.add_trace(go.Scatter(x=road["x"], y=road["y"], mode='lines', line=dict(color='#111', width=40), hoverinfo='skip'))

    # Idea 15: Neural Ghost Path (Non-Adaptive Baseline)
    if ghost_data['x']:
        fig.add_trace(go.Scatter(x=ghost_data['x'], y=ghost_data['y'], mode='lines', 
                                 line=dict(color='rgba(255, 75, 75, 0.4)', width=1, dash='dot'), name="Standard Baseline"))

    # HAWK Active Trajectory
    if path_data['x']:
        fig.add_trace(go.Scatter(x=path_data['x'], y=path_data['y'], mode='lines', 
                                 line=dict(color='#00FF41', width=3), name="HAWK Active Trail"))

    # Idea 7: 4D Spatial Knowledge (Perception Bubble)
    fig.add_shape(type="circle", xref="x", yref="y", x0=uav_pos[0]-perception_range, y0=uav_pos[1]-perception_range,
                  x1=uav_pos[0]+perception_range, y1=uav_pos[1]+perception_range, line_color="#00FF41", opacity=0.2)

    # Landmarks
    for lm in CITY_DATA["landmarks"]:
        fig.add_trace(go.Scatter(x=[lm["pos"][0]], y=[lm["pos"][1]], mode='text', text=[lm["icon"]],
                                 textfont=dict(size=30), name=lm["name"], hovertemplate=f"{lm['name']}<extra></extra>"))

    # Idea 10: Hazard Injection
    for h in hazards:
        fig.add_trace(go.Scatter(x=[h['x']], y=[h['y']], mode='text', text=["🚧"], textfont=dict(size=35)))

    # UAV Agent
    fig.add_trace(go.Scatter(x=[uav_pos[0]], y=[uav_pos[1]], mode='markers+text', text=["<b>X</b>"],
                             marker=dict(size=20, color="white", symbol="x-thin-open"), textfont=dict(color="white", size=18)))

    fig.update_layout(template="plotly_dark", xaxis=dict(range=[0, 50], showgrid=False, zeroline=False),
                      yaxis=dict(range=[0, 50], showgrid=False, zeroline=False), height=750, 
                      margin=dict(l=0,r=0,t=0,b=0), showlegend=False, hovermode="closest")
    return fig
