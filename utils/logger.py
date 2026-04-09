import os
import json
from datetime import datetime

def save_run_metrics(metrics):
    os.makedirs("data/run_logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"data/run_logs/run_{timestamp}.json"
    with open(path, "w") as f:
        json.dump(metrics, f, indent=4)

def update_heading_state(next_heading):
    state_path = "data/run_logs/run_state.json"
    state = {"last_heading": next_heading}
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)

def get_last_heading():
    state_path = "data/run_logs/run_state.json"
    if not os.path.exists(state_path):
        return None
    with open(state_path, "r") as f:
        return json.load(f).get("last_heading")



# import csv
# import os


# def log_collision(filepath, position):
#     """
#     Save collision position into CSV file
#     """

#     # Ensure folder exists
#     os.makedirs(os.path.dirname(filepath), exist_ok=True)

#     file_exists = os.path.isfile(filepath)

#     with open(filepath, mode='a', newline='') as file:
#         writer = csv.writer(file)

#         # Write header only if file doesn't exist
#         if not file_exists:
#             writer.writerow(["x", "y", "z"])

#         writer.writerow(position)