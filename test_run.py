import json
from hawk_system.hawk_controller import HawkController

print("Loading config...")

with open("config.json") as f:
    config = json.load(f)

print("Initializing system...")

hawk = HawkController(config)

print("Starting system...")

hawk.run()