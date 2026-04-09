import time
import cv2
import numpy as np


class PerceptionManager:

    """
    Central perception pipeline.

    Responsibilities:
    - run detection
    - filter low-quality detections
    - normalize outputs
    - update landmark memory
    - provide clean perception results
    - support panoramic perception
    - future-ready for semantic reasoning
    """

    def __init__(
        self,
        landmark_detector,
        landmark_memory,
        min_confidence=0.6
    ):

        self.detector = landmark_detector
        self.memory = landmark_memory
        self.min_confidence = min_confidence

    # --------------------------------------------------

    def perceive(self, frame, drone_position=None, drone_yaw=None):

        """
        Full perception pipeline

        FIXED + STABLE VERSION:
        - correct image format for YOLO
        - no duplicate processing
        - safe detection handling
        - clean output
        """

        # --------------------------------------------------
        # STEP 0: IMAGE SAFETY CHECK
        # --------------------------------------------------

        if frame is None:
            print("[ERROR] Frame is None")
            return []

        # --------------------------------------------------
        # STEP 1: FIX IMAGE FORMAT (CRITICAL)
        # --------------------------------------------------

        # Ensure uint8 (YOLO requirement)
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        # Ensure 3 channels
        if len(frame.shape) == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # Convert BGR → RGB (ONLY ONCE)
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"[ERROR] Color conversion failed: {e}")
            return []

        # --------------------------------------------------
        # STEP 2: DEBUG INFO
        # --------------------------------------------------

        try:
            print("[DEBUG] Frame shape:", frame.shape)
        except:
            print("[ERROR] Invalid frame format")
            return []
        
        cv2.imwrite("debug_frame.png", frame)  # Save debug frame for inspection

        # --------------------------------------------------
        # STEP 3: DETECTION
        # --------------------------------------------------

        try:
            detections = self.detector.detect(
                frame,
                drone_position=drone_position,
                drone_yaw=drone_yaw
            )

            print("[DEBUG] Detector output:", detections)

        except Exception as e:
            print(f"[ERROR] Detection failed: {e}")
            return []

        # --------------------------------------------------
        # STEP 4: POST-PROCESSING
        # --------------------------------------------------

        processed = []

        for d in detections:

            confidence = d.get("confidence", 0)
            label = d.get("label")

            # ---------- CONFIDENCE FILTER ----------
            if confidence < self.min_confidence:
                continue

            # ---------- LABEL CHECK ----------
            if not label:
                continue

            # ---------- NORMALIZATION ----------
            normalized = self._normalize_detection(d)

            processed.append(normalized)

            # --------------------------------------------------
            # MEMORY UPDATE (SAFE)
            # --------------------------------------------------

            if drone_position is not None:

                try:
                    self.memory.add_landmark(
                        normalized["label"],
                        list(drone_position),
                        yaw=drone_yaw,
                        confidence=confidence
                    )
                except Exception:
                    pass

        # --------------------------------------------------
        # DEBUG FINAL OUTPUT
        # --------------------------------------------------

        print("[DEBUG] Filtered detections:", processed)

        return processed

    # --------------------------------------------------

    def panoramic_perception(self, client, capture_func, drone_position=None):

        """
        360° perception scan

        Used for:
        - initial exploration
        - target scanning
        """

        all_detections = []

        yaw_angles = [0, 90, 180, 270]

        for yaw in yaw_angles:

            try:
                client.rotateToYawAsync(yaw).join()
            except:
                pass

            frame = capture_func(client)

            if frame is None:
                print("[ERROR] Frame is None")
                continue

            detections = self.perceive(
                frame,
                drone_position=drone_position,
                drone_yaw=yaw
            )

            all_detections.extend(detections)

        return all_detections

    # --------------------------------------------------

    def _normalize_detection(self, detection):

        """
        Clean detection structure
        (future-ready for embeddings / clustering)
        """

        return {
            "label": detection.get("label"),
            "color": detection.get("color"),
            "confidence": detection.get("confidence"),
            "bbox": detection.get("bbox"),
            "timestamp": time.time()
        }

    # --------------------------------------------------

    def find_target(self, detections, target_label):

        """
        Find matching object in detections
        Supports partial + exact match
        """

        for d in detections:

            label = d.get("label")

            if not label:
                continue

            if target_label == label or target_label in label:
                return d

        return None