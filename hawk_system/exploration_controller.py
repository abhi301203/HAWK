import time
import numpy as np
from utils.camera_utils import capture_frame


class ExplorationController:

    """
    Handles full exploration loop:
    - grid traversal
    - image capture
    - landmark detection
    - frontier navigation
    """

    def __init__(
        self,
        client,
        movement,
        visit_map,
        map_metadata,
        frontier_detector,
        frontier_cluster,
        frontier_utility,
        capture,
        metrics,
        landmark_detector,
        landmark_memory,
        vln_controller,
        altitudes,
        grid_size,
        step_size,
        speed,
        max_runtime,
        max_images,
        capture_four,
        start_heading
    ):

        self.client = client
        self.movement = movement

        self.visit_map = visit_map
        self.map_metadata = map_metadata

        self.frontier_detector = frontier_detector
        self.frontier_cluster = frontier_cluster
        self.frontier_utility = frontier_utility

        self.capture = capture
        self.metrics = metrics

        self.landmark_detector = landmark_detector
        self.landmark_memory = landmark_memory

        self.vln_controller = vln_controller

        self.altitudes = altitudes
        self.grid_size = grid_size
        self.step_size = step_size
        self.speed = speed

        self.max_runtime = max_runtime
        self.max_images = max_images
        self.capture_four = capture_four

        self.start_heading = start_heading

        self.previous_frontier = None

    # --------------------------------------------------

    def run(self):

        yaw_map = {
            "North": 0,
            "East": 90,
            "South": 180,
            "West": 270
        }

        # ---------- SAFE TAKEOFF ----------
        try:
            print("[INFO] Taking off for exploration...")
            self.client.takeoffAsync().join()
        except:
            pass

        try:
            self.client.rotateToYawAsync(yaw_map[self.start_heading]).join()
        except Exception:
            pass

        start_time = time.time()

        start_pos = self.movement.get_position()
        start_x, start_y = start_pos

        max_frontier_moves = 50
        frontier_moves = 0

        half = self.grid_size // 2
        offsets = np.arange(-half, half + self.step_size, self.step_size)

        for z in self.altitudes:

            self.movement.move_to_altitude(z)

            try:
                self.client.hoverAsync().join()
            except:
                pass

            time.sleep(0.5)

            direction = 1

            for y_offset in offsets:

                for x_offset in offsets[::direction]:

                    frontier_target = None

                    # ---------- LIMIT CHECKS ----------

                    if time.time() - start_time > self.max_runtime:
                        return

                    if self.capture.image_count >= self.max_images:
                        return

                    target_x = start_x + x_offset
                    target_y = start_y + y_offset

                    # ---------- COLLISION FILTER ----------

                    if self.visit_map and hasattr(self.visit_map, "visit_penalty"):

                        penalty = self.visit_map.visit_penalty(target_x, target_y)

                        if penalty > 10:
                            continue

                    # ---------- MOVE ----------

                    success, distance = self.movement.move_to(
                        target_x,
                        target_y,
                        z,
                        self.speed
                    )

                    print(f"[MOVE] → ({target_x:.2f}, {target_y:.2f}) | success={success}")

                    if not success:
                        continue

                    # ---------- VISIT ----------

                    self.visit_map.mark_visited(target_x, target_y)

                    try:
                        self.vln_controller.spatial_graph.add_node((target_x, target_y))
                    except:
                        pass

                    self.map_metadata.update_cell(target_x, target_y)

                    self.frontier_cluster.previous_cell = (target_x, target_y)

                    self.metrics.grid_completed += 1
                    self.metrics.distance_travelled += distance

                    # ---------- IMAGE + DETECTION ----------

                    try:

                        self.client.hoverAsync().join()
                        time.sleep(0.2)

                        # self.capture.capture(self.capture_four)

                        # frame = capture_frame(self.client)

                        self.capture.capture(self.capture_four)

                        # use latest captured image (SAFE)
                        image_ids = getattr(self.capture, "last_capture_ids", [])

                        frame = None

                        if image_ids:
                            import os, cv2
                            image_path = os.path.join(self.capture.run_folder, image_ids[-1])
                            frame = cv2.imread(image_path)

                        drone_pos = self.movement.get_position()

                        detections = self.landmark_detector.detect(
                            frame,
                            drone_position=drone_pos
                        )

                        print(f"[DEBUG] Exploration detections: {detections}")

                        for d in detections:

                            if d.get("confidence", 0) < 0.4:
                                continue

                            label = d.get("label")

                            if label:
                                self.landmark_memory.add_landmark(
                                    label,
                                    list(drone_pos)
                                )

                        image_ids = getattr(self.capture, "last_capture_ids", [])

                        self.map_metadata.update_images(
                            target_x,
                            target_y,
                            image_ids,
                            altitude=z,
                            yaw_list=[0, 90, 180, 270] if self.capture_four else None
                        )

                        self.metrics.images_captured = self.capture.image_count

                    except Exception as e:
                        print(f"Capture error: {e}")

                    # ---------- FRONTIER ----------

                    if self.metrics.grid_completed % 3 == 0:

                        frontiers = self.frontier_detector.detect_frontiers()

                        if frontiers:

                            current_x, current_y = self.movement.get_position()

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

                    # ---------- EXECUTE FRONTIER ----------

                    if frontier_target:

                        if frontier_moves >= max_frontier_moves:
                            continue

                        frontier_moves += 1

                        fx, fy = frontier_target

                        if self.previous_frontier:

                            px, py = self.previous_frontier

                            if abs(px - fx) < 0.5 and abs(py - fy) < 0.5:
                                continue

                        success_frontier, dist = self.movement.move_to(
                            fx,
                            fy,
                            z,
                            self.speed
                        )

                        if success_frontier:

                            self.visit_map.mark_visited(fx, fy)

                            try:
                                self.vln_controller.spatial_graph.add_node((fx, fy))
                            except:
                                pass

                            self.map_metadata.update_cell(fx, fy)

                            self.metrics.distance_travelled += dist

                            self.previous_frontier = (fx, fy)

                direction *= -1