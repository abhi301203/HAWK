import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from phase3.path_memory_engine import PathMemoryEngine
from phase3.landmark_memory import LandmarkMemory
from phase3.spatial_memory_graph import SpatialMemoryGraph


class VLNNavigationPlanner:

    """
    Hybrid VLN Navigation Planner

    Combines:
    - path memory reuse
    - landmark viewpoint navigation
    - spatial graph planning
    - object search fallback
    """

    def __init__(self):

        self.path_memory = PathMemoryEngine()

        self.landmark_memory = LandmarkMemory()

        self.graph = SpatialMemoryGraph()

    # --------------------------------------------------

    def search_mode(self, current_position):

        """
        Levy-style random exploration when object is unknown
        """

        dx = random.uniform(-25, 25)
        dy = random.uniform(-25, 25)

        target = (
            current_position[0] + dx,
            current_position[1] + dy
        )

        print("\nSearch mode activated → exploring:", target)

        return [target]

    # --------------------------------------------------

    def plan_navigation(self, instruction_data, current_position):

        if instruction_data is None:
            return None

        instruction_text = instruction_data.get("instruction")

        # --------------------------------------------------
        # 1 PATH MEMORY REUSE
        # --------------------------------------------------

        stored_path = self.path_memory.search_path(instruction_text)

        if stored_path is not None:

            print("\nPath memory match found")

            return stored_path

        # --------------------------------------------------
        # 2 LANDMARK TARGET SEARCH
        # --------------------------------------------------

        landmarks = instruction_data.get("landmarks", [])

        if len(landmarks) > 0:

            landmark_name = landmarks[0]

            landmark = self.landmark_memory.nearest_landmark(
                landmark_name,
                current_position
            )

            if landmark:

                target = tuple(landmark["pos"])

                print("\nLandmark target located:", target)

                # --------------------------------------------------
                # 3 GRAPH NAVIGATION
                # --------------------------------------------------

                path = self.graph.astar_path(
                    current_position,
                    target
                )

                if path is None:

                    path = self.graph.dijkstra_path(
                        current_position,
                        target
                    )

                return path

        # --------------------------------------------------
        # 4 SEARCH MODE (fallback)
        # --------------------------------------------------

        return self.search_mode(current_position)


# --------------------------------------------------
# Test block
# --------------------------------------------------

if __name__ == "__main__":

    planner = VLNNavigationPlanner()

    instruction = {
        "instruction": "go to the building",
        "actions": ["go"],
        "landmarks": ["building"],
        "directions": []
    }

    current_pos = (0, 0)

    path = planner.plan_navigation(
        instruction,
        current_pos
    )

    print("\nGenerated Path:\n")
    print(path)