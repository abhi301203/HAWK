import time
import os
from datetime import datetime
import airsim

from core.system_orchestrator import SystemOrchestrator

from utils.camera_utils import capture_frame
from utils.heading import resolve_heading
from utils.metrics import MetricsLogger

from navigation.movement import DroneMovement
from navigation.escape import EscapeSystem

from mapping.visit_map import VisitMapManager
from mapping.collision_memory import CollisionMemory
from mapping.frontier_detector import FrontierDetector
from mapping.frontier_cluster import FrontierCluster
from mapping.frontier_utility import FrontierUtility
from map_metadata_manager import MapMetadataManager
from entropy_map import EntropyMap

from perception.image_capture import ImageCaptureManager

from phase2.domain_detector import DomainDetector

from phase3.vln_navigation_controller import VLNNavigationController
from phase3.runtime_instruction_interface import RuntimeInstructionInterface
from phase3.landmark_memory import LandmarkMemory
from phase3.landmark_detector import LandmarkDetector

from hawk_system.warmup_explorer import WarmupExplorer
from hawk_system.exploration_controller import ExplorationController
from hawk_system.shutdown_manager import ShutdownManager
from hawk_system.vln_task_executor import VLNTaskExecutor
from hawk_system.object_search import ObjectSearch
from hawk_system.perception_manager import PerceptionManager
from hawk_system.frontier_manager import FrontierManager



class HawkController:

    def __init__(self, config):

        print("Initializing HAWK System")

        # ---------------- CONFIG ----------------
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
        self.vln_warmup_time = run.get("vln_warmup_seconds", 20)  # reduced

        self.capture_four = move["capture_four_directions"]
        self.speed = move["movement_speed"]

        # ---------------- RUN DIRECTORY ----------------
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.run_folder = os.path.join(
            "data", "raw_images", self.domain, f"run_{timestamp}"
        )
        os.makedirs(self.run_folder, exist_ok=True)

        # ---------------- AIRSIM ----------------
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

        # ---------------- CORE ----------------
        self.visit_map = VisitMapManager()
        self.entropy_map = EntropyMap(self.visit_map)
        self.metrics = MetricsLogger(self.domain)

        self.visit_map.set_metrics_logger(self.metrics)

        self.collision_memory = CollisionMemory(self.metrics)

        self.movement = DroneMovement(
            self.client, self.collision_memory, self.metrics
        )

        self.escape = EscapeSystem(self.client)

        self.capture = ImageCaptureManager(self.client, self.run_folder)

        self.map_metadata = MapMetadataManager(
            self.visit_map, self.collision_memory, self.capture
        )

        # ---------------- FRONTIER ----------------
        self.frontier_detector = FrontierDetector(self.visit_map)
        self.frontier_cluster = FrontierCluster(
            self.visit_map, self.collision_memory, self.entropy_map
        )
        self.frontier_utility = FrontierUtility(
            self.visit_map, self.collision_memory
        )

        # ---------------- VLN ----------------
        self.instruction_interface = RuntimeInstructionInterface()
        self.landmark_memory = LandmarkMemory()

        self.landmark_detector = LandmarkDetector(
            landmark_memory=self.landmark_memory
        )

        # perception pipeline
        self.perception_manager = PerceptionManager(
            self.landmark_detector,
            self.landmark_memory
        )

        # lightweight frontier manager (for VLN search only)
        self.frontier_manager = FrontierManager()

        self.vln_controller = VLNNavigationController(
            self.movement, self.speed, self.altitudes[0]
        )

        self.perception_manager = PerceptionManager(
            self.landmark_detector,
            self.landmark_memory
        )

        self.frontier_manager = FrontierManager()

        # ---------- OBJECT SEARCH INITIALIZATION ----------

        self.object_search = ObjectSearch(
            perception_manager=self.perception_manager,
            movement=self.movement,
            frontier_manager=self.frontier_manager,
            image_capture_manager=self.capture
        )
        # self.object_search = ObjectSearch(
        #     perception_manager=self.perception_manager,
        #     movement=self.movement,
        #     frontier_manager=self.frontier_manager
        # )

        self.vln_executor = VLNTaskExecutor(
            self.movement,
            self.landmark_memory,
            self.landmark_detector,
            self.vln_controller,
            search_function=self.object_search,
            altitude=self.altitudes[0],
            speed=self.speed
        )

        # ✅ FIXED: Proper initialization
        self.domain_detector = DomainDetector(self.client)

        print("[DEBUG] ObjectSearch initialized with capture:", type(self.capture))


        # ---------------- MODULES ----------------
        self.warmup_explorer = WarmupExplorer(
            self.movement,
            self.visit_map,
            self.map_metadata,
            self.vln_controller,
            self.step_size,
            self.altitudes[0],
            self.speed,
            self.vln_warmup_time
        )

        self.exploration_controller = ExplorationController(
            self.client,
            self.movement,
            self.visit_map,
            self.map_metadata,
            self.frontier_detector,
            self.frontier_cluster,
            self.frontier_utility,
            self.capture,
            self.metrics,
            self.landmark_detector,
            self.landmark_memory,
            self.vln_controller,
            self.altitudes,
            self.grid_size,
            self.step_size,
            self.speed,
            self.max_runtime,
            self.max_images,
            self.capture_four,
            resolve_heading()[0]
        )

        self.shutdown_manager = ShutdownManager(
            self.client,
            self.visit_map,
            self.capture,
            self.map_metadata,
            self.metrics
        )

        # ---------------- PHASE 2 ----------------
        self.system_orchestrator = SystemOrchestrator()

        self.state = "IDLE"

    # --------------------------------------------------

    def run(self):

        print("\nStarting HAWK Controller...")

        try:
            self.client.takeoffAsync().join()
        except Exception as e:
            print(f"Takeoff failed: {e}")
            return

        start_time = time.time()

        instruction_data = self._get_instruction()

        # ================= COMMAND =================
        if instruction_data["type"] == "command":
            self._handle_command(instruction_data["value"])
            return self.shutdown_manager.shutdown(start_time)

        # ================= EXPLORATION =================
        if instruction_data["type"] == "exploration":

            self.state = "EXPLORATION"
            print("\n[MODE] Exploration Mode Activated")

            # -------- DOMAIN DETECTION --------
            try:
                domain = self.domain_detector.detect(self.client, self.capture.get_frame)
                print(f"Detected domain: {domain}")
                self.domain = domain
            except Exception as e:
                print(f"Domain detection failed: {e}")

            # -------- LOAD DOMAIN KNOWLEDGE --------
            print("[INFO] Loading domain knowledge...")

            # -------- RUN EXPLORATION --------
            try:
                self.exploration_controller.run()
            except Exception as e:
                print(f"Exploration error: {e}")

            # -------- 🔥 PHASE 2 PIPELINE --------
            print("\n[PHASE 2] Running dataset pipeline...")
            try:
                self.system_orchestrator.handle_exploration_cycle()
            except Exception as e:
                print(f"Phase2 error: {e}")

            return self.shutdown_manager.shutdown(start_time)

        # ================= VLN =================
        if instruction_data["type"] == "navigation":

            self.state = "VLN_TASK"
            instruction = instruction_data["value"]

            print(f"\n[MODE] VLN Navigation Mode: {instruction}")

            # -------- WARMUP --------
            try:
                self.warmup_explorer.run()
            except Exception as e:
                print(f"Warmup error: {e}")

            # -------- EXECUTE VLN --------
            try:
                map_cells = self._get_map_cells()
                self.vln_executor.execute(instruction, map_cells)

                print("\nHolding position after task...")
                try:
                    self.client.hoverAsync().join()
                except:
                    pass

                time.sleep(3)

            except Exception as e:
                print(f"VLN error: {e}")

            # -------- 🔥 PHASE 2 PIPELINE --------
            print("\n[PHASE 2] Updating knowledge...")
            try:
                self.system_orchestrator.handle_exploration_cycle()
            except Exception as e:
                print(f"Phase2 error: {e}")

            return self.shutdown_manager.shutdown(start_time)

        # # ================= COMMAND =================
        # if instruction_data["type"] == "command":
        #     self._handle_command(instruction_data["value"])
        #     return self.shutdown_manager.shutdown(start_time)

        # # ================= VLN =================
        # if instruction_data["type"] == "navigation":

        #     self.state = "VLN_TASK"
        #     instruction = instruction_data["value"]

        #     if isinstance(instruction, dict):
        #         instruction_text = instruction.get("value", "")
        #     else:
        #         instruction_text = instruction

        #     print(f"\nVLN Mode: {instruction_text}")

        #     # ✅ SHORT SAFE WARMUP (NOT EXPLORATION)
        #     try:
        #         self.warmup_explorer.run()
        #     except Exception as e:
        #         print(f"Warmup error: {e}")

        #     try:
        #         map_cells = self._get_map_cells()
        #         self.vln_executor.execute(instruction, map_cells)

        #         # ---------- 🔥 NEW FIX: HOLD EXECUTION ----------
        #         print("\nHolding position after task...")

        #         try:
        #             self.client.hoverAsync().join()
        #         except:
        #             pass

        #         time.sleep(5)  # allow movement to complete

        #     except Exception as e:
        #         print(f"VLN error: {e}")

        #     return self.shutdown_manager.shutdown(start_time)

        # # ================= EXPLORATION =================
        # self.state = "EXPLORATION"
        # print("\nExploration Mode Activated")

        # try:
        #     domain = self.domain_detector.detect(self.client, capture_frame)
        #     print(f"Detected domain: {domain}")
        #     self.domain = domain
        # except Exception as e:
        #     print(f"Domain detection failed: {e}")

        # try:
        #     self.exploration_controller.run()
        # except Exception as e:
        #     print(f"Exploration error: {e}")

        # return self.shutdown_manager.shutdown(start_time)

    # --------------------------------------------------

    def _get_instruction(self):

        try:
            raw = self.instruction_interface.get_instruction()

            if raw is None:
                return {"type": "exploration", "value": None}

            instruction = str(raw).strip()

            # ---------- EMPTY → EXPLORATION ----------
            if instruction == "":
                return {"type": "exploration", "value": None}

            instruction_lower = instruction.lower()

            # ---------- COMMAND ----------
            if instruction_lower in ["help", "status", "memory", "exit"]:
                return {"type": "command", "value": instruction_lower}

            # ---------- NAVIGATION ----------
            return {"type": "navigation", "value": instruction}

        except Exception as e:
            print(f"[Instruction Error]: {e}")
            return {"type": "exploration", "value": None}

    # --------------------------------------------------

    def _handle_command(self, command):

        print(f"\nCommand: {command}")

        if command == "status":
            print(f"State: {self.state}")

        elif command == "memory":
            print(list(self.landmark_memory.landmarks.keys()))

    # --------------------------------------------------

    def _get_map_cells(self):

        try:
            data = self.map_metadata.data.get("cells", {})
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    # --------------------------------------------------

    # def _search_object_wrapper(self, target_label):

    #     from hawk_system.object_search import ObjectSearch

    #     search_engine = ObjectSearch(
    #         self.client,
    #         self.movement,
    #         self.landmark_detector,
    #         self.landmark_memory,
    #         self.frontier_detector,
    #         self.frontier_cluster,
    #         self.frontier_utility,
    #         self.vln_controller,
    #         self.altitudes[0],
    #         self.speed
    #     )

    #     return search_engine.search(target_label)