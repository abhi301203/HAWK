import os
import json
import numpy as np


class NavigationExperienceMemory:

    """
    Stores navigation experience during VLN runs.

    Records:
    - drone path waypoints
    - object observation locations
    """

    def __init__(self,
                 memory_dir="data/navigation_memory",
                 waypoint_distance=5):

        self.memory_dir = memory_dir
        self.waypoint_distance = waypoint_distance

        os.makedirs(memory_dir, exist_ok=True)

        self.path_file = os.path.join(memory_dir, "drone_paths.json")
        self.object_file = os.path.join(memory_dir, "object_memory.json")

        self.path_memory = []
        self.object_memory = {}

        self.load_memory()

    # --------------------------------------------------

    def load_memory(self):

        if os.path.exists(self.path_file):

            with open(self.path_file, "r") as f:
                self.path_memory = json.load(f)

        if os.path.exists(self.object_file):

            with open(self.object_file, "r") as f:
                self.object_memory = json.load(f)

    # --------------------------------------------------

    def save_memory(self):

        with open(self.path_file, "w") as f:
            json.dump(self.path_memory, f, indent=4)

        with open(self.object_file, "w") as f:
            json.dump(self.object_memory, f, indent=4)

    # --------------------------------------------------

    def store_waypoint(self, position):

        """
        Store drone position every few meters
        """

        if len(self.path_memory) == 0:

            self.path_memory.append(position)
            self.save_memory()
            return

        last = np.array(self.path_memory[-1])
        current = np.array(position)

        dist = np.linalg.norm(current - last)

        if dist >= self.waypoint_distance:

            self.path_memory.append(position)
            self.save_memory()

    # --------------------------------------------------

    def store_object_observation(self, label, position, yaw):

        """
        Store location where drone saw an object
        """

        if label not in self.object_memory:

            self.object_memory[label] = []

        record = {
            "pos": position,
            "yaw": yaw
        }

        self.object_memory[label].append(record)

        self.save_memory()

    # --------------------------------------------------

    def get_object_locations(self, label):

        return self.object_memory.get(label, [])

    # --------------------------------------------------

    def nearest_object_location(self, label, current_position):

        points = self.object_memory.get(label, [])

        if len(points) == 0:
            return None

        best = None
        best_dist = float("inf")

        for p in points:

            pos = np.array(p["pos"])
            dist = np.linalg.norm(pos - np.array(current_position))

            if dist < best_dist:

                best_dist = dist
                best = p

        return best