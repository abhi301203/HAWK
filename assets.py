import plotly.graph_objects as go

# IDEA 4 & 7: DIGITAL TWIN SPATIAL MAP
CITY_ASSETS = {
    "infrastructure": {
        "roads": {"x": [0, 50, None, 25, 25], "y": [25, 25, None, 0, 50]},
        "buildings": [
            {"name": "HOME", "pos": [45, 5], "icon": "🏠", "desc": "80-Sector-A"},
            {"name": "HOSPITAL", "pos": [5, 45], "icon": "🏥", "desc": "10-North-Blvd"},
            {"name": "SCHOOL", "pos": [35, 45], "icon": "🏫", "desc": "70-Education"},
            {"name": "PARK", "pos": [10, 10], "icon": "🌳", "desc": "Central-Green"}
        ]
    },
    "hazards": [{"name": "OBSTACLE", "pos": [20, 25], "icon": "🚧"}]
}

def create_world_view(drone_pos, trail_x, trail_y, ghost_x, ghost_y, show_hazards=False):
    fig = go.Figure()
    # Roads
    fig.add_trace(go.Scatter(x=CITY_ASSETS["infrastructure"]["roads"]["x"], 
                             y=CITY_ASSETS["infrastructure"]["roads"]["y"], 
                             mode='lines', line=dict(color='#1a1a1a', width=60), hoverinfo='skip'))

    # IDEA 15: NEURAL GHOST PATH (The Counter-Factual Path)
    if ghost_x is not None:
        fig.add_trace(go.Scatter(x=ghost_x, y=ghost_y, mode='lines', 
                                 line=dict(color='#ff4b4b', width=1, dash='dot'), name="Non-Adaptive Path"))
    
    if trail_x is not None:
        fig.add_trace(go.Scatter(x=trail_x, y=trail_y, mode='lines', 
                                 line=dict(color='#00FF41', width=3), name="HAWK AI Path"))

    for b in CITY_ASSETS["infrastructure"]["buildings"]:
        fig.add_trace(go.Scatter(x=[b["pos"][0]], y=[b["pos"][1]], mode='text', 
                                 text=[b["icon"]], textfont=dict(size=30), name=b["name"]))
    
    # IDEA 10: STRESS-TESTER
    if show_hazards:
        for h in CITY_ASSETS["hazards"]:
            fig.add_trace(go.Scatter(x=[h["pos"][0]], y=[h["pos"][1]], mode='text', 
                                     text=[h["icon"]], textfont=dict(size=30), name="Static Hazard"))

    # UAV MARKER (Idea 16)
    fig.add_trace(go.Scatter(x=[drone_pos[0]], y=[drone_pos[1]], mode='markers+text', 
                             text=["X"], textfont=dict(color="white", size=20, family="Arial Black"),
                             marker=dict(size=18, color="white", symbol="x-thin-open")))

    fig.update_layout(template="plotly_dark", xaxis=dict(range=[0, 50], showgrid=False), 
                      yaxis=dict(range=[0, 50], showgrid=False), height=650, 
                      margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
    return fig
