import airsim
import json
import time
import numpy as np
import os
from datetime import datetime

from navigation.movement import DroneMovement
from navigation.escape import EscapeSystem
from perception.image_capture import ImageCaptureManager
from mapping.visit_map import VisitMapManager
from mapping.collision_memory import CollisionMemory
from mapping.frontier_detector import FrontierDetector
from mapping.frontier_utility import FrontierUtility
from mapping.frontier_cluster import FrontierCluster
from map_metadata_manager import MapMetadataManager
from entropy_map import EntropyMap
from utils.heading import resolve_heading
from utils.metrics import MetricsLogger
from utils.camera_utils import capture_frame
from phase2.domain_detector import DomainDetector
from phase3.vln_navigation_controller import VLNNavigationController
from phase3.runtime_instruction_interface import RuntimeInstructionInterface
from phase3.landmark_memory import LandmarkMemory
from phase3.landmark_detector import LandmarkDetector
from core.system_orchestrator import SystemOrchestrator


class HawkPhase1:

    def __init__(self, config):

        print("Initializing HAWK Phase 1")

        self.config = config
        self.domain = config["domain_name"]

        env = config["environment_settings"]
        run = config["run_limits"]
        move = config["movement_settings"]

        self.grid_size = env["grid_size"]
        self.step_size = env["step_size"]
        self.altitudes = env["altitudes"]

        self.max_images = run["max_images_per_run"]
        self.max_runtime = run["max_runtime_minutes"] * 60

        self.vln_warmup_time = run.get("vln_warmup_seconds", 60)  # seconds of exploration before allowing VLN instructions

        self.capture_four = move["capture_four_directions"]
        self.speed = move["movement_speed"]
        # exploration confidence used by frontier selection and adaptation
        self.exploration_confidence = 0.5

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.run_folder = os.path.join(
            "data",
            "raw_images",
            self.domain,
            f"run_{timestamp}"
        )

        os.makedirs(self.run_folder, exist_ok=True)

        # ---------------- AIRSIM ----------------

        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

        print("Exploring..!")

        # ---------------- MODULES ----------------

        self.visit_map = VisitMapManager()  # visit map

        self.entropy_map = EntropyMap(self.visit_map)  # entropy map

        self.metrics = MetricsLogger(self.domain)  # metrics

        self.visit_map.set_metrics_logger(self.metrics)

        self.collision_memory = CollisionMemory(self.metrics)  # collision memory

        self.movement = DroneMovement(      # movement system
            self.client,
            self.collision_memory,
            self.metrics
        )

        self.escape = EscapeSystem(self.client)  # escape system

        self.capture = ImageCaptureManager(   # image capture system
            self.client, 
            self.run_folder
        )
        
        self.map_metadata = MapMetadataManager(self.visit_map, self.collision_memory, self.capture)  # map metadata manager

        self.frontier_detector = FrontierDetector(self.visit_map)
        self.frontier_utility = FrontierUtility(self.visit_map, self.collision_memory)
        self.frontier_cluster = FrontierCluster(self.visit_map, self.collision_memory, self.entropy_map)  # frontier clustering system
        
        # ------------------ VLN MODULES ------------------

        self.instruction_interface = RuntimeInstructionInterface()  # interface to receive instructions at runtime

        self.landmark_memory = LandmarkMemory()  # memory to store landmark information

        self.landmark_detector = LandmarkDetector(landmark_memory=self.landmark_memory)  # landmark detection system with memory integration

        self.vln_controller = VLNNavigationController(  # VLN navigation controller
            self.movement,
            self.speed,
            self.altitudes[0],
        )

        self.start_heading, self.heading_cycle = resolve_heading()

        # remember previous frontier to avoid oscillation (or) frontier oscillation guard
        self.previous_frontier = None

        # ------------------- NAVIGATION STATE MANAGER ----------------------

        # Tracks system operating mode
        self.state = "IDLE"

        # ------------------- DOMAIN ADAPTION MODULE ----------------------
        
        #initialize domain detector once (avoid repeated creation during runtime)
        domain = self.domain_detector.detect(self.client, capture_frame)

    # --------------------------------------------------

    def vln_warmup_exploration(self):

        """
        Smart exploration pattern used before VLN execution.
        Uses expanding square search.
        """

        print("\nStarting smart warmup exploration...")

        start_time = time.time()

        radius = self.step_size

        while time.time() - start_time < self.vln_warmup_time:

            current_pos = self.movement.get_position()

            cx, cy = current_pos

            # expanding square pattern
            targets = [
                (cx + radius, cy),
                (cx, cy + radius),
                (cx - radius, cy),
                (cx, cy - radius)
            ]

            for tx, ty in targets:

                success, _ = self.movement.move_to(
                    tx,
                    ty,
                    self.altitudes[0],
                    self.speed
                )

                if success:

                    self.visit_map.mark_visited(tx, ty)

                    self.map_metadata.update_cell(tx, ty)

                    # update VLN spatial graph
                    self.vln_controller.spatial_graph.add_node(tx, ty)

            radius += self.step_size

        print("Warmup exploration finished")

    # --------------------------------------------------

    def search_for_target_object(self, target_label):

        """
        Frontier-guided object search with safety limits.
        Prevents infinite exploration.
        """

        start_pos = self.movement.get_position()
        start_time = time.time()

        print(f"\nSearching for target object: {target_label}")

        max_search_steps = 5
        max_search_radius = 80      # meters
        max_search_time = 120       # seconds

        visited_frontiers = set()

        for _ in range(max_search_steps):

            # ----------------------------------
            # SAFETY CHECK 1: TIME LIMIT
            # ----------------------------------

            if time.time() - start_time > max_search_time:
                print("Search stopped: time limit reached")
                return None

            # ----------------------------------
            # SAFETY CHECK 2: DISTANCE LIMIT
            # ----------------------------------

            current_pos = self.movement.get_position()

            dist = np.linalg.norm(
                np.array(current_pos) - np.array(start_pos)
            )

            if dist > max_search_radius:
                print("Search stopped: radius limit reached")
                return None

            # ----------------------------------
            # 1️⃣ PANORAMIC SCAN
            # ----------------------------------

            detections = self.landmark_detector.panoramic_scan(
                self.client,
                capture_frame,
                drone_position=current_pos
            )

            for d in detections:

                label = d["label"]

                color = d.get("color", None)

                # vehicle_alias = ["car", "truck", "bus", "vehicle"]

                # if target_label in label or label in target_label or label in vehicle_alias :
                if target_label == label or target_label in label:

                    print(f"\nTarget detected: {label}")

                    pos = self.movement.get_position()

                    # store landmark memory
                    self.landmark_memory.add_landmark(
                        label,
                        list(pos)
                    )

                    return pos

            # ----------------------------------
            # 2️⃣ MOVE TOWARD FRONTIER
            # ----------------------------------

            frontiers = self.frontier_detector.detect_frontiers()

            if frontiers:

                best_cluster = self.frontier_cluster.best_cluster(
                    current_pos[0],
                    current_pos[1],
                    frontiers
                )

                if best_cluster:

                    frontier_target = self.frontier_utility.compute_utility(
                        current_pos[0],
                        current_pos[1],
                        best_cluster
                    )

                    if frontier_target:

                        fx, fy = frontier_target

                        frontier_key = (round(fx), round(fy))

                        # ----------------------------------
                        # SAFETY CHECK 3: AVOID REPEATING FRONTIER
                        # ----------------------------------

                        if frontier_key in visited_frontiers:
                            continue

                        visited_frontiers.add(frontier_key)

                        print(f"\nMoving toward frontier: {fx}, {fy}")

                        success, _ = self.movement.move_to(
                            fx,
                            fy,
                            self.altitudes[0],
                            self.speed
                        )

                        if success:

                            self.visit_map.mark_visited(fx, fy)

                            self.map_metadata.update_cell(fx, fy)

                            self.vln_controller.spatial_graph.add_node(
                                fx,
                                fy
                            )

                            continue

            # ----------------------------------
            # 3️⃣ FALLBACK RANDOM SCAN
            # ----------------------------------

            yaw = np.random.uniform(-180, 180)

            try:
                self.client.rotateToYawAsync(yaw).join()
            except:
                pass

        print(f"Target object '{target_label}' not found "
              f"after {max_search_steps} search attemps.")

        return None

    # --------------------------------------------------

    def run(self):

        self.client.takeoffAsync().join()

        # ----------------- CHECK FOR USER INSTRUCTION (VLN MODE) ----------------

        instruction_data = self.instruction_interface.get_instruction()

        if instruction_data and instruction_data["type"] == "instruction":

            instruction = instruction_data["value"]

            self.state = "VLN_TASK"

            print("\nVLN instruction received:", instruction)

            print("\nRunning automatic exploration warmup...")

            self.vln_warmup_exploration()

            # ------------------------------------------
            # PROCESS INSTRUCTION (WITH DECOMPOSITION)
            # ------------------------------------------

            instruction_data = self.vln_controller.process_instruction(instruction)

            subtasks = instruction_data.get("subtasks", [])

            for task in subtasks:

                landmarks = task.get("landmarks", [])

                if landmarks:

                    target = landmarks[0]

                    print(f"\nSearching for landmark: {target}")

                    # ------------------------------------------
                    # CHECK LANDMARK MEMORY FIRST
                    # ------------------------------------------

                    current_pos = self.movement.get_position()

                    memory_entry = self.landmark_memory.nearest_landmark(
                        target,
                        current_pos
                    )

                    if memory_entry:

                        print("\nKnown landmark found in memory")

                        target_pos = memory_entry["pos"]

                        self.movement.move_to(
                            target_pos[0],
                            target_pos[1],
                            self.altitudes[0],
                            self.speed
                        )

                        continue


                    # ------------------------------------------
                    # OTHERWISE SEARCH OBJECT
                    # ------------------------------------------

                    target_pos = self.search_for_target_object(target)

                    if target_pos:

                        print("\nTarget found. Moving toward object...")

                        self.movement.move_to(
                            target_pos[0],
                            target_pos[1],
                            self.altitudes[0],
                            self.speed
                        )

                        # store object coordinate memory
                        self.landmark_memory.add_landmark(
                            target,
                            list(target_pos)
                        )

                        continue

            # ------------------------------------------
            # FALLBACK: GRAPH NAVIGATION
            # ------------------------------------------

            try:

                map_cells = self.map_metadata.data.get("cells", {})

                if not isinstance(map_cells, dict):
                    map_cells = {}

                self.vln_controller.execute_navigation(
                    instruction,
                    map_cells,
                    self.landmark_memory,
                )

                print("\nVLN task completed")

            except Exception as e:

                print("\nVLN execution error:", e)

            return

        # instruction = self.instruction_interface.get_instruction()

        # if instruction:

        #     print("\nVLN instruction received:", instruction)

        #     print("\nRunning automatic exploration warmup...")

        #     warmup_start = time.time()

        #     while time.time() - warmup_start < self.vln_warmup_time:

        #         # simple random exploration move
        #         current_pos = self.movement.get_position()

        #         rx = np.random.uniform(-self.step_size, self.step_size)
        #         ry = np.random.uniform(-self.step_size, self.step_size)

        #         target_x = current_pos[0] + rx
        #         target_y = current_pos[1] + ry

        #         success, _ = self.movement.move_to(
        #             target_x,
        #             target_y,
        #             self.altitudes[0],
        #             self.speed
        #         )

        #         if success:

        #             self.visit_map.mark_visited(target_x, target_y)

        #             self.map_metadata.update_cell(target_x, target_y)

        #             # update spatial graph for VLN
        #             self.vln_controller.spatial_graph.add_node(
        #                 target_x,
        #                 target_y
        #             )

        #     print("\nWarmup exploration complete")

        #     try:

        #         map_cells = self.map_metadata.data.get("cells", {})

        #         if not isinstance(map_cells, dict):
        #             map_cells = {}

        #         self.vln_controller.execute_navigation(
        #             instruction,
        #             map_cells,
        #             self.landmark_memory,
        #         )

        #         print("\nVLN task completed")

        #     except Exception as e:

        #         print("\nVLN execution error:", e)

        #     return

        # ----------------- ENVIRONMENT DOMAIN DETECTION ----------------

        self.state = "EXPLORATION"

        print("Detecting environment domain...")

        # detector = DomainDetector(self.client)

        # capture_frame comes from utils.camera_utils and handles safe capture and returns the image frame for domain detection
        domain = domain_detector.detect(self.client, capture_frame)
                                

        print("Detected domain:", domain)

        self.domain = domain

        yaw_map = {
            "North": 0,
            "East": 90,
            "South": 180,
            "West": 270
        }

        self.client.rotateToYawAsync(yaw_map[self.start_heading]).join()

        start_time = time.time()

        start_pos = self.movement.get_position()
        start_x, start_y = start_pos

        # Frontier exploration safety budget
        max_frontier_moves = 50
        frontier_moves = 0

        # ---------- GRID OFFSETS ----------

        half = self.grid_size // 2
        offsets = np.arange(-half, half + self.step_size, self.step_size)

        for z in self.altitudes:

            self.movement.move_to_altitude(z)

            # stabilize after altitude change
            self.client.hoverAsync().join()
            time.sleep(0.5)

            direction = 1

            for y_offset in offsets:

                for x_offset in offsets[::direction]:

                    frontier_target = None

                    # ---------- RUNTIME LIMIT ----------

                    if time.time() - start_time > self.max_runtime:
                        return self.finish(start_time)

                    if self.capture.image_count >= self.max_images:
                        return self.finish(start_time)

                    target_x = start_x + x_offset
                    target_y = start_y + y_offset

                    # ---------- COLLISION MEMORY FILTER ----------

                    if self.collision_memory.is_collision_zone(target_x, target_y):
                        self.metrics.frontier_blocked_by_collision += 1
                        continue

                    # ---------- VISIT PENALTY ----------

                    penalty = self.visit_map.visit_penalty(target_x, target_y)

                    if penalty > 10:
                        continue

                    self.metrics.grid_attempted += 1

                    success, distance = self.movement.move_to(
                        target_x,
                        target_y,
                        z,
                        self.speed
                    )

                    if not success:
                        continue

                    # ---------- MARK VISITED ----------

                    self.visit_map.mark_visited(target_x, target_y)

                    # update spatial navigation graph
                    self.vln_controller.spatial_graph.add_node((target_x, target_y))

                    self.map_metadata.update_cell(target_x, target_y)

                    # update exploration direction
                    self.frontier_cluster.previous_cell = (target_x, target_y)

                    self.metrics.grid_completed += 1
                    self.metrics.distance_travelled += distance

                    # ---------- IMAGE CAPTURE ----------

                    try:

                        self.client.hoverAsync().join()
                        time.sleep(0.2)

                        # capture images
                        self.capture.capture(self.capture_four)

                        # -------------- LANDMARK DETECTION --------------

                        frame = capture_frame(self.client)

                        drone_pos = self.movement.get_position()

                        detections = self.landmark_detector.detect(frame, drone_position=drone_pos)

                        for d in detections:

                            label = d["label"]
                            self.landmark_memory.add_landmark(label, drone_pos)

                            if d["confidence"] < 0.6:
                                continue

                        # get captured image ids safely
                        image_ids = getattr(self.capture, "last_capture_ids", [])

                        # update map metadata with images
                        self.map_metadata.update_images(
                            target_x,
                            target_y,
                            image_ids,
                            altitude=z,
                            yaw_list=[0, 90, 180, 270] if self.capture_four else None
                        )

                        # ---------- EXPLORATION SUCCESS FLAG ----------
                        try:

                            gx = int(round(target_x / self.visit_map.grid_resolution))
                            gy = int(round(target_y / self.visit_map.grid_resolution))

                            key = f"{gx}_{gy}"

                            if key in self.map_metadata.data["cells"]:

                                if image_ids:
                                    self.map_metadata.data["cells"][key]["exploration_success"] = 1

                        except:
                            pass

                        # update metrics
                        self.metrics.images_captured = self.capture.image_count

                    except Exception as e:

                        print(f"Error during capture: {e}")
                    # ---------- FRONTIER NAVIGATION ----------

                    if self.metrics.grid_completed % 3 == 0:

                        frontiers = self.frontier_detector.detect_frontiers()

                        if frontiers:

                            self.metrics.decision_count += 1

                            current_x, current_y = self.movement.get_position()

                            # ---------- CLUSTER FRONTIERS ----------

                            best_cluster = self.frontier_cluster.best_cluster(
                                current_x,
                                current_y,
                                frontiers
                            )

                            if best_cluster:

                                frontier_target = self.frontier_utility.compute_utility(
                                    current_x,
                                    current_y,
                                    best_cluster
                                )

                    # ---------- EXECUTE FRONTIER MOVE ----------

                    if frontier_target is not None:

                        if frontier_moves >= max_frontier_moves:

                            print("Frontier exploration budget reached")
                            frontier_target = None
                            continue

                        frontier_moves += 1

                        # ---------- FRONTIER OSCILLATION GUARD ----------

                        fx, fy = frontier_target

                        if self.previous_frontier is not None and frontier_target is not None:

                            fx, fy = frontier_target

                            px, py = self.previous_frontier

                            if abs(px - fx) < 0.5 and abs(py - fy) < 0.5:
                                continue

                        self.metrics.frontier_targets_selected += 1

                        success_frontier, frontier_distance = self.movement.move_to(
                            fx,
                            fy,
                            z,
                            self.speed
                        )

                        if success_frontier:

                            self.visit_map.mark_visited(fx, fy)

                            self.vln_controller.spatial_graph.add_node(fx, fy)

                            self.map_metadata.update_cell(fx, fy)

                            self.metrics.distance_travelled += frontier_distance

                            # store frontier to prevent oscillation
                            self.previous_frontier = (fx, fy)

                            # record cluster success
                            self.frontier_cluster.record_cluster_result(fx, fy, 1)

                        else:

                            # record cluster failure
                            self.frontier_cluster.record_cluster_result(fx, fy, 0)

                    # ---------- IMAGE LIMIT SAFETY ----------

                    if self.capture.image_count >= self.max_images:
                        return self.finish(start_time)

                direction *= -1

        return self.finish(start_time)

    # --------------------------------------------------

    def finish(self, start_time):

        runtime = time.time() - start_time
        
        # save exploration data 
        self.visit_map.save()

        self.capture.save_metadata()

        self.map_metadata.save()

        # compute metrics
        self.metrics.total_yaw_rotations = self.capture.yaw_rotation_count

        metrics = self.metrics.compute(runtime)

        # land drone 
        self.client.landAsync().join()

        # ensure drone fully reaches the ground
        try:
            pos = self.client.getMultirotorState().kinematics_estimated.position
            self.client.moveToZAsync(0, 1).join()
        except:
            pass

        # shutdown
        self.client.armDisarm(False)
        self.client.enableApiControl(False)

        print("\nPHASE 1 COMPLETE")
        print(metrics)

        return metrics


# --------------------------------------------------

if __name__ == "__main__":

    print("STARTING HAWK")

    with open("config.json") as f:
        config = json.load(f)

    # initialize autonomous orchestrator
    orchestrator = SystemOrchestrator()

    hawk = HawkPhase1(config)

    hawk.run()

    # automatic dataset pipeline check
    orchestrator.handle_exploration_cycle()
