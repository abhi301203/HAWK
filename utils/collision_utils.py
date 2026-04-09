import numpy as np
import json
import os

def is_new_collision(position, zones, radius):
    for z in zones:
        if np.linalg.norm(np.array(position) - np.array(z)) < radius:
            return False
    return True

def save_collision_memory(zones):
    os.makedirs("data/collision_logs", exist_ok=True)
    path = "data/collision_logs/collision_memory.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            existing = json.load(f)
    else:
        existing = []
    existing.extend(zones)
    with open(path, "w") as f:
        json.dump(existing, f, indent=4)