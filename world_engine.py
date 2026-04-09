import plotly.graph_objects as go
import numpy as np

# Idea 4: Comprehensive Environment Dataset
ENVIRONMENT_CONFIG = {
    "zones": [
        {"name": "Industrial Sector", "x": [0, 15, 15, 0], "y": [35, 35, 50, 50], "color": "rgba(255, 0, 0, 0.05)"},
        {"name": "Residential Sector", "x": [35, 50, 50, 35], "y": [0, 0, 15, 15], "color": "rgba(0, 255, 255, 0.05)"},
        {"name": "The Pond", "x": [30, 40, 40, 30], "y": [30, 30, 40, 40], "color": "rgba(0, 100, 255, 0.2)"}
    ],
    "nodes": [
        {"name": "BASE_STATION", "pos": [2, 2], "icon": "🛰️"},
        {"name": "HOSPITAL", "pos": [5, 45], "icon": "🏥"},
        {"name": "SCHOOL", "pos": [35, 45], "icon": "🏫"},
        {"name": "HOME", "pos": [45, 5], "icon": "🏠"},
        {"name": "WAREHOUSE", "pos": [12, 38], "icon": "🏭"}
    ],
    "roads": [
        {"x": [0, 50], "y": [25, 25]}, {"x": [25, 25], "y": [0, 50]},
        {"x": [0, 50], "y": [5, 5]}, {"x": [5, 5], "y": [0, 50]}
    ]
}

def render_sovereign_map(uav_pos, active_path, ghost_path, obstacles):
    """Idea 7 & 15: Interactive 4D Knowledge Visualization."""
    fig = go.Figure()
    
    # 1. Zone Rendering
    for zone in ENVIRONMENT_CONFIG["zones"]:
        fig.add_trace(go.Scatter(x=zone["x"], y=zone["y"], fill="toself", fillcolor=zone["color"], line=dict(width=0), name=zone["name"]))

    # 2. Infrastructure (Road Bias)
    for road in ENVIRONMENT_CONFIG["roads"]:
        fig.add_trace(go.Scatter(x=road["x"], y=road["y"], mode='lines', line=dict(color='#111', width=50), hoverinfo='skip'))

    # 3. Idea 15: Ghost Path Logic (Comparison)
    if ghost_path is not None and len(ghost_path['x']) > 0:
        fig.add_trace(go.Scatter(x=ghost_path['x'], y=ghost_path['y'], mode='lines', 
                                 line=dict(color='rgba(255, 75, 75, 0.3)', width=1, dash='dot'), name="Baseline UAV"))

    # 4. HAWK Path Logic
    if active_path is not None and len(active_path['x']) > 0:
        fig.add_trace(go.Scatter(x=active_path['x'], y=active_path['y'], mode='lines', 
                                 line=dict(color='#00FF41', width=3), name="HAWK AI"))

    # 5. Node Injection
    for node in ENVIRONMENT_CONFIG["nodes"]:
        fig.add_trace(go.Scatter(x=[node["pos"][0]], y=[node["pos"][1]], mode='text', text=[node["icon"]],
                                 textfont=dict(size=35), name=node["name"], hovertemplate=f"{node['name']}<extra></extra>"))

    # 6. UAV 'X' Mark
    fig.add_trace(go.Scatter(x=[uav_pos[0]], y=[uav_pos[1]], mode='markers+text', text=["<b>X</b>"],
                             marker=dict(size=25, color="white", symbol="x-thin-open"), textfont=dict(color="white", size=20)))

    fig.update_layout(template="plotly_dark", xaxis=dict(range=[0, 50], showgrid=False, zeroline=False),
                      yaxis=dict(range=[0, 50], showgrid=False, zeroline=False), height=800, 
                      margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
    return fig
