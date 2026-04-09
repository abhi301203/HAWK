import airsim
import time
import os
import numpy as np


class ObjectSearch:

    """
    Stable Intelligent Object Search

    Core Idea:
    ----------
    This module performs ACTIVE perception-based object search
    when:
    - memory is weak or unreliable
    - object is not immediately visible

    Strategy:
    ----------
    perception → consistency → estimate → move → expand → repeat

    Key Features:
    ----------
    - Multi-frame detection stability (reduces false positives)
    - Lightweight 3D position estimation from 2D bbox
    - Progressive search expansion
    - Safe movement (no async conflicts)
    - Frontier fallback (last resort)
    """

    def __init__(
        self,
        perception_manager,
        movement,
        frontier_manager=None,
        image_capture_manager=None,
        max_attempts=5,
        consistency_frames=3,
        min_confidence=0.4,   # lowered → improves recall (important)
        search_radius=5
    ):

        # Core modules
        self.perception = perception_manager
        self.movement = movement
        self.frontier_manager = frontier_manager
        self.capture_manager = image_capture_manager

        # Search configuration
        self.max_attempts = max_attempts              # total search cycles
        self.consistency_frames = consistency_frames  # frames per attempt
        self.min_confidence = min_confidence          # detection threshold
        self.base_radius = search_radius              # movement radius

        self.altitude = getattr(self.movement, "altitude", 5)
        self.speed = getattr(self.movement, "speed", 2)

    # --------------------------------------------------

    # --------------------------------------------------
    # ROAD HEURISTIC (LIGHTWEIGHT SEMANTIC REASONING)
    # --------------------------------------------------

    def _is_road_like(self, detection):
        """
        Simple heuristic to detect road-like regions

        Uses:
        - wide horizontal bbox
        - low vertical height
        """

        try:
            bbox = detection.get("bbox")

            if not bbox:
                return False

            x1, y1, x2, y2 = bbox

            width = abs(x2 - x1)
            height = abs(y2 - y1)

            # road-like: wide + flat
            if width > 2 * height:
                return True

        except:
            pass

        return False

    # --------------------------------------------------

    def _estimate_object_position(self, bbox, current_pos, yaw):

        """
        Estimate object world position from bounding box

        Idea:
        -----
        Convert 2D image detection → approximate 3D world position

        Assumptions:
        - fixed camera FOV
        - fixed approximate distance
        - bbox center → direction

        NOTE:
        This is a lightweight approximation (no depth sensor used)
        """

        try:
            x1, y1, x2, y2 = bbox

            # center of detected object in image
            cx = (x1 + x2) / 2

            # assume image width (AirSim default)
            image_width = 256

            # normalize to [-1, 1] range
            offset = (cx - image_width / 2) / (image_width / 2)

            # convert offset → angle deviation
            angle = yaw + (offset * 45)  # ±45° field assumption

            import math

            # assumed distance to object (tunable parameter)
            distance = 6

            dx = distance * math.cos(math.radians(angle))
            dy = distance * math.sin(math.radians(angle))

            return (
                current_pos[0] + dx,
                current_pos[1] + dy
            )

        except Exception as e:
            print(f"Position estimation error: {e}")
            return None

    # --------------------------------------------------

    def search(self, target_label, map_metadata=None, landmark_memory=None):

        """
        Main object search loop

        Pipeline:
        ----------
        1. Capture frames
        2. Run perception
        3. Filter detections
        4. Check consistency
        5. Estimate object position
        6. Move / expand search
        """

        print(f"\nSearching for target object: {target_label}")

        attempt = 0
        radius = self.base_radius

        while attempt < self.max_attempts:

            print(f"[Search Attempt {attempt + 1}]")

            current_pos = self.movement.get_position()
            detections_accum = []
            found = False

            # --------------------------------------------------
            # STEP 1: MULTI-FRAME PERCEPTION
            # --------------------------------------------------
            # WHY:
            # Single frame detection is noisy → use multiple frames
            # to stabilize detection
            # --------------------------------------------------

            for _ in range(self.consistency_frames):

                # --------------------------------------------------
                #  PANORAMIC PERCEPTION (FROM hawk_train)
                # --------------------------------------------------

                try:
                    detections = self.perception.panoramic_perception(
                        self.movement.client,
                        lambda client: self._capture_wrapper(client),
                        drone_position=current_pos
                    )
                except Exception as e:
                    print(f"Panoramic perception error: {e}")
                    detections = []

                print("Detections:", detections)

                detections_accum.extend(detections)

                time.sleep(0.2)

            # --------------------------------------------------
            # STEP 2: FILTER DETECTIONS
            # --------------------------------------------------
            # WHY:
            # remove:
            # - wrong labels
            # - low confidence detections
            # --------------------------------------------------

            candidates = []

            for d in detections_accum:

                label = d.get("label")
                confidence = d.get("confidence", 0)

                if not label:
                    continue

                # -----------------------------
                # TARGET MATCH
                # -----------------------------
                # if target_label not in label :
                #     continue

                # -----------------------------
                # SMART LABEL MATCHING
                # -----------------------------
                label = label.lower()
                target = target_label.lower()

                aliases = {
                    "car": ["car", "vehicle", "truck", "bus"],
                    "person": ["person", "human", "pedestrian"],
                    "tree": ["tree", "plant"]
                }

                valid_labels = aliases.get(target, [target])

                if not any(v in label for v in valid_labels):
                    continue

                if confidence < self.min_confidence:
                    continue

                # -----------------------------
                #  ROAD REASONING FOR CAR
                # -----------------------------
                if target_label == "car":

                    # If detection is weak → require road context
                    if confidence < 0.7:

                        if not self._is_road_like(d):
                            print("Rejected car (not road-like context)")
                            continue

                candidates.append(d)

            # --------------------------------------------------
            # STEP 3: CONSISTENCY SCORING
            # --------------------------------------------------
            # WHY:
            # true object appears multiple times consistently
            # fake detection appears randomly
            # --------------------------------------------------

            best_candidate = None
            best_score = 0

            if candidates:

                grouped = {}

                for c in candidates:
                    key = c["label"]
                    grouped.setdefault(key, []).append(c)

                for label, group in grouped.items():

                    count = len(group)
                    avg_conf = np.mean([g["confidence"] for g in group])

                    score = count * avg_conf

                    if score > best_score:
                        best_score = score
                        best_candidate = group[0]

            # --------------------------------------------------
            # STEP 4: TARGET FOUND
            # --------------------------------------------------

            if best_candidate:

                print("Target locked via stable detection")

                found = True

                # ---------- GET DRONE ORIENTATION ----------
                try:
                    state = self.movement.client.getMultirotorState()
                    orientation = state.kinematics_estimated.orientation

                    yaw_rad = airsim.to_eularian_angles(orientation)[2]
                    yaw = yaw_rad * (180.0 / 3.14159265)

                except Exception as e:
                    print("Yaw error:", e)
                    yaw = 0

                bbox = best_candidate.get("bbox")

                if not bbox:
                    return None

                # ---------- CONVERT DETECTION → WORLD POSITION ----------
                estimated_pos = self._estimate_object_position(
                    bbox,
                    current_pos,
                    yaw
                )

                if estimated_pos:
                    print("Estimated object position:", estimated_pos)
                    return estimated_pos

                return None

            # --------------------------------------------------
            # STEP 5: LOCAL SEARCH MOVEMENT
            # --------------------------------------------------
            # WHY:
            # if object not found → explore nearby region first
            # --------------------------------------------------

            if not found:
                print("Target not stable → searching nearby region")

            cx, cy = current_pos

            # -----------------------------
            #  ROAD BIAS MOVEMENT
            # -----------------------------
            offsets = []

            if target_label == "car":

                # forward bias (assume road ahead)
                offsets = [
                    (radius, 0),     # forward
                    (radius, radius/2),
                    (radius, -radius/2),
                    (0, radius),
                    (0, -radius),
                    (-radius, 0)
                ]

            else:

                offsets = [
                    (radius, 0),
                    (0, radius),
                    (-radius, 0),
                    (0, -radius)
                ]

            moved = False

            for dx, dy in offsets:

                tx = cx + dx
                ty = cy + dy

                try:
                    success, _ = self.movement.move_to(
                        tx,
                        ty,
                        getattr(self.movement, "altitude", 5),
                        getattr(self.movement, "speed", 3)
                    )

                    time.sleep(0.5)

                except Exception as e:
                    print(f"Movement error: {e}")
                    success = False

                if success:
                    moved = True
                    break

            ## -----------------------------------------
            # ROAD HEURISTIC (FIXED)
            # -----------------------------------------

            if target_label == "car":

                print("[INFO] Car search → applying road bias")

                forward_targets = [
                    (cx + radius * 2, cy),
                    (cx + radius, cy + radius),
                    (cx + radius, cy - radius)
                ]

                for tx, ty in forward_targets:
                    try:
                        success, _ = self.movement.move_to(
                            tx,
                            ty,
                            self.altitude,
                            self.speed
                        )
                        if success:
                            moved = True
                            break
                    except:
                        continue

                if moved:
                    attempt += 1
                    continue

            # --------------------------------------------------
            # STEP 6: FRONTIER FALLBACK
            # --------------------------------------------------
            # WHY:
            # if local movement fails → use intelligent exploration
            # --------------------------------------------------

            if not moved and self.frontier_manager and map_metadata:

                print("Fallback to frontier search")

                try:
                    frontier = self.frontier_manager.select_frontier(
                        current_pos,
                        map_metadata,
                        landmark_memory,
                        target_label
                    )
                except Exception:
                    frontier = None

                if frontier:

                    fx, fy = frontier

                    try:
                        self.movement.move_to(
                            fx,
                            fy,
                            getattr(self.movement, "altitude", 5),
                            getattr(self.movement, "speed", 3)
                        )

                        time.sleep(0.5)

                    except Exception:
                        pass

            # expand search radius progressively
            radius += self.base_radius
            attempt += 1

        print("Target object not found after search attempts")
        return None

    # --------------------------------------------------

    def _capture_wrapper(self, client):

        """
        Safe image capture wrapper

        WHY:
        Avoid:
        - async crashes
        - missing images
        - invalid paths
        """

        if self.capture_manager is None:
            print("No capture manager attached")
            return None

        try:
            self.capture_manager.capture(capture_four=False)

            image_ids = getattr(self.capture_manager, "last_capture_ids", [])

            if not image_ids:
                return None

            image_name = image_ids[-1]

            image_path = os.path.join(
                self.capture_manager.run_folder,
                image_name
            )

            import cv2
            img = cv2.imread(image_path)

            return img

        except Exception as e:
            print(f"Capture wrapper error: {e}")
            return None