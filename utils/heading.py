import json
import os

HEADINGS = ["North", "East", "South", "West"]


def resolve_heading():

    path = "data/run_logs/run_state.json"

    state = {"last_heading": "North"}

    if os.path.exists(path):

        try:
            with open(path) as f:
                state = json.load(f)

        except:
            pass

    last = state.get("last_heading", "North")

    idx = (HEADINGS.index(last) + 1) % 4

    new_heading = HEADINGS[idx]

    os.makedirs("data/run_logs", exist_ok=True)

    with open(path, "w") as f:

        json.dump({"last_heading": new_heading}, f, indent=4)

    return new_heading, idx