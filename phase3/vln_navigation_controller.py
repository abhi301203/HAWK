import sys
import os
import random
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from phase3.instruction_parser import InstructionParser
from phase3.hybrid_instruction_memory import HybridInstructionMemory
from phase3.path_memory_engine import PathMemoryEngine
from phase3.frontier_exploration_controller import FrontierExplorationController
from phase3.spatial_memory_graph import SpatialMemoryGraph


class VLNNavigationController:

    """
    Hybrid VLN Navigation Controller

    Capabilities:
    - instruction parsing
    - instruction memory
    - path memory reuse
    - object landmark navigation
    - object search behaviour
    - frontier exploration
    - spatial graph path planning
    - drone movement execution
    """

    def __init__(self, movement_system, speed, altitude, cluster_memory=None):

        self.parser = InstructionParser()
        self.instruction_memory = HybridInstructionMemory()
        self.path_memory = PathMemoryEngine()
        self.frontier_controller = FrontierExplorationController()
        self.spatial_graph = SpatialMemoryGraph()
        self.cluster_memory = cluster_memory

        self.movement = movement_system
        self.speed = speed
        self.altitude = altitude

    # -----------------------------------------------------

    def process_instruction(self, instruction):

        """
        Parse instruction into clean structured subtasks.
        Ensures compatibility with VLN executor.
        """

        if not instruction or not isinstance(instruction, str):
            return {"subtasks": []}

        instruction = instruction.lower().strip()

        # ---------- SIMPLE SPLIT ----------
        parts = instruction.split(" and ")

        subtasks = []

        for p in parts:

            words = p.strip().split()

            if not words:
                continue

            # ---------- BASIC OBJECT EXTRACTION ----------
            # last word = target object (safe fallback)
            target = words[-1]

            # clean unwanted characters
            target = target.replace("'", "").replace("}", "").replace("{", "")

            # remove common noise words
            if target in ["to", "the", "a", "an"]:
                continue

            subtasks.append({
                "landmarks": [target]
            })

        # ---------- FINAL SAFETY ----------
        if not subtasks:
            words = instruction.split()
            if words:
                target = words[-1]
                target = target.replace("'", "").replace("}", "").replace("{", "")

                subtasks = [{
                    "landmarks": [target]
                }]

        # ---------- STORE IN MEMORY ----------
        try:
            self.instruction_memory.add_instruction({
                "text": instruction,
                "subtasks": subtasks
            })
        except:
            pass

        return {
            "subtasks": subtasks
        }

    # def process_instruction(self, instruction):

    #     """
    #     Parse instruction and split into sub-tasks.
    #     """

    #     parsed = self.parser.parse(instruction)

    #     subtasks = []

    #     # simple decomposition by keywords
    #     parts = instruction.lower().split(" and ")

    #     for p in parts:

    #         sub = self.parser.parse(p)

    #         subtasks.append(sub)

    #     try:
    #         self.instruction_memory.add_instruction(parsed)
    #     except:
    #         pass

    #     return {
    #         "original": parsed,
    #         "subtasks": subtasks
    #     }

    # -----------------------------------------------------

    def check_path_memory(self, instruction):

        """
        Check if a similar instruction path already exists
        """

        try:

            record = self.path_memory.search_path(instruction)

            if record:

                print("\nReusing path from memory")

                if isinstance(record, dict):

                    return record.get("path")

                return record

        except Exception:
            pass

        return None

    # -----------------------------------------------------

    def search_object_mode(self, current_position):

        """
        Simple Levy-style search movement when object not found. or controlled search when object is unknown.
        """

        print("Object not known. Activating search mode.")

        search_radius = 12

        angle = random.uniform(0,2 * 3.1415)

        # random direction movement (Levy style)
        # dx = random.uniform(-search_radius, search_radius)
        # dy = random.uniform(-search_radius, search_radius)
        dx = search_radius * np.cos(angle)
        dy = search_radius * np.sin(angle)

        target = (
            current_position[0] + dx,
            current_position[1] + dy
        )

        return [target]

    # -----------------------------------------------------

    def plan_navigation(
        self,
        instruction,
        map_metadata,
        landmark_memory,
        current_position
    ):

        parsed = self.process_instruction(instruction)

        original = parsed.get("original", {})

        instruction_landmarks = original.get("landmarks", [])
        instruction_colors = original.get("colors", [])

        # -------------------------------------------------
        # 1️⃣ PATH MEMORY REUSE
        # -------------------------------------------------

        path_record = self.check_path_memory(instruction)

        if path_record:

            print("Using stored path from memory")

            if isinstance(path_record, dict):
                return path_record.get("path")

            return path_record

        # -------------------------------------------------
        # 2️⃣ OBJECT LANDMARK MEMORY
        # -------------------------------------------------

        if len(instruction_landmarks) > 0:

            label = instruction_landmarks[0]

            landmark = landmark_memory.nearest_landmark(
                label,
                current_position
            )

            if landmark:

                print("Using stored landmark for:", label)

                target = landmark["pos"]

                path = self.spatial_graph.astar_path(
                    tuple(current_position),
                    tuple(target)
                )

                if path is None:
                    
                    path = self.spatial_graph.dijkstra_path(
                        tuple(current_position),
                        tuple(target)
                    )

                return path
            
        
        # -------------------------------------------------
        # 2️⃣.1️⃣ CLUSTER MEMORY NAVIGATION
        # -------------------------------------------------

        if len(instruction_landmarks) > 0 and self.cluster_memory:

            label = instruction_landmarks[0]

            cluster = self.cluster_memory.get_best_cluster(
                label,
                current_position
            )

            if cluster:

                print("Using cluster memory for:", label)

                target = cluster["centroid"]

                path = self.spatial_graph.astar_path(
                    tuple(current_position),
                    tuple(target)
                )

                if path is None:

                    path = self.spatial_graph.dijkstra_path(
                        tuple(current_position),
                        tuple(target)
                    )

                if path:
                    return path

        # -------------------------------------------------
        # 3️⃣ FRONTIER EXPLORATION
        # -------------------------------------------------

        best_frontier = self.frontier_controller.select_next_frontier(
            map_metadata,
            instruction_landmarks,
            landmark_memory
        )

        if best_frontier:

            path = self.spatial_graph.astar_path(
                tuple(current_position),
                tuple(best_frontier)
            )

            if path is None:

                path = self.spatial_graph.dijkstra_path(
                    tuple(current_position),
                    tuple(best_frontier)
                )

            return path

        # -------------------------------------------------
        # 4️⃣ OBJECT SEARCH MODE
        # -------------------------------------------------

        return self.search_object_mode(current_position)

    # -----------------------------------------------------

    def execute_navigation(
        self,
        instruction,
        map_metadata,
        landmark_memory
    ):

        current_position = self.movement.get_position()

        path = self.plan_navigation(
            instruction,
            map_metadata,
            landmark_memory,
            current_position
        )

        # ------------ PATH VALIDATION -------------

        if path is None or len(path) == 0:

            print("No path generated")

            return
        
        # ------------ PATH LENGTH SAFETY -------------

        max_steps = 50

        if len(path) > max_steps:

            print("Path too long. Truncating.")

            path = path[:max_steps]

        print("\nExecuting VLN path:", path)

        for waypoint in path:

            waypoint = tuple(waypoint)

            x, y = waypoint

            success, distance = self.movement.move_to(
                x,
                y,
                self.altitude,
                self.speed
            )

            if not success:

                print("Movement failed at waypoint:", waypoint)
                break

        try:
            
            self.path_memory.add_path(instruction, path)

        except: 
            pass

        print("\nNavigation completed")


# -----------------------------------------------------

if __name__ == "__main__":

    print("VLN Navigation Controller loaded successfully")