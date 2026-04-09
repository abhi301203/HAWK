import json
import os


class CollisionMemory:

    def __init__(self, metrics = None):

        self.path = "data/collision_logs/collision_memory.json"

        os.makedirs("data/collision_logs", exist_ok=True)

        self.metrics = None

        if os.path.exists(self.path):

            with open(self.path) as f:
                self.data = json.load(f)

        else:

            self.data = []

    def set_metrics_logger(self, metrics_logger):

        self.metrics = metrics_logger

    def save(self):

        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def register_collision(self, x, y, radius=1.5):

        point = [float(x), float(y)]

        # prevent duplicates
        for cx, cy in self.data:

            dx = point[0] - cx
            dy = point[1] - cy

            if (dx * dx + dy * dy) ** 0.5 < radius:
                return

        self.data.append(point)

        self.save()

        try:
            self.metrics.collision_zones_created += 1
        except:
            pass

    def is_collision_zone(self, x, y, z=None):

        if not self.data:
            return False

        horizontal_radius = 2.0   # meters
        vertical_height = 10.0    # meters

        for px, py in self.data:

            dx = x - px
            dy = y - py

            horizontal_distance = (dx * dx + dy * dy) ** 0.5

            if horizontal_distance < horizontal_radius:
                return True

        return False