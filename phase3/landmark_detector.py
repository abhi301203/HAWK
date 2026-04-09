import cv2
import numpy as np
from ultralytics import YOLO
from nltk.corpus import wordnet


class LandmarkDetector:

    """
    Enhanced Landmark Detector (STABLE + SEMANTIC)

    Improvements:
    - strict label filtering
    - bbox size filtering (removes far noise)
    - duplicate suppression
    - semantic validation
    - stable perception output
    """

    def __init__(
        self,
        model_name="yolov8n.pt",
        conf_threshold=0.5,
        landmark_memory=None,
        cluster_memory=None
    ):

        print("Initializing Landmark Detector...")

        self.model = YOLO(model_name)
        self.conf_threshold = conf_threshold

        self.landmark_memory = landmark_memory
        self.cluster_memory = cluster_memory

        # IMPORTANT: allowed classes (reduces noise massively)
        self.VALID_LABELS = {
            "car", "truck", "bus", "person",
            "bicycle", "motorbike"
        }

    # -----------------------------------------------------

    def preprocess(self, frame):
        return frame 
        # return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # -----------------------------------------------------

    def normalize_label(self, label):

        try:
            synsets = wordnet.synsets(label)

            if synsets:
                return label  # avoid over-generalization

        except Exception:
            pass

        return label

    # -----------------------------------------------------

    def detect_color(self, frame, bbox):

        x1, y1, x2, y2 = map(int, bbox)

        h, w = frame.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        roi = frame[y1:y2, x1:x2]

        if roi.size == 0:
            return None

        hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
        avg_color = hsv.mean(axis=(0, 1))
        hue = avg_color[0]

        if hue < 10 or hue > 160:
            return "red"
        if 10 < hue < 25:
            return "orange"
        if 25 < hue < 35:
            return "yellow"
        if 35 < hue < 85:
            return "green"
        if 85 < hue < 125:
            return "blue"
        if 125 < hue < 170:
            return "purple"

        return "unknown"

    # -----------------------------------------------------

    def _is_valid_bbox(self, bbox, frame_shape):

        """
        Remove tiny / far detections (VERY IMPORTANT)
        """

        x1, y1, x2, y2 = bbox
        area = (x2 - x1) * (y2 - y1)

        h, w = frame_shape[:2]
        image_area = h * w

        # reject too small objects (<1% of image)
        if area < 0.01 * image_area:
            return False

        return True

    # -----------------------------------------------------

    def detect(self, frame, drone_position=None, drone_yaw=None):

        frame = self.preprocess(frame)

        if frame is None or frame.size == 0:
            return []

        results = self.model(frame, verbose=False)

        detections = []
        seen_centers = []

        for r in results:

            if r.boxes is None:
                continue

            for box in r.boxes:

                confidence = float(box.conf[0])

                if confidence < self.conf_threshold:
                    continue

                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]

                label = label.lower().strip() #normalize labels

                if label in ["automobile", "vehicle"]:
                    label = "car"

                normalized_label = self.normalize_label(label)

                # ---------- STRICT CLASS FILTER ----------
                if normalized_label not in self.VALID_LABELS:
                    continue

                bbox = box.xyxy[0].tolist()

                # ---------- SIZE FILTER ----------
                if not self._is_valid_bbox(bbox, frame.shape):
                    continue

                # ---------- DUPLICATE FILTER ----------
                cx = (bbox[0] + bbox[2]) / 2
                cy = (bbox[1] + bbox[3]) / 2

                duplicate = False
                for px, py in seen_centers:
                    if abs(cx - px) < 20 and abs(cy - py) < 20:
                        duplicate = True
                        break

                if duplicate:
                    continue

                seen_centers.append((cx, cy))

                color = self.detect_color(frame, bbox)

                detection = {
                    "label": normalized_label,
                    "color": color,
                    "confidence": confidence,
                    "bbox": bbox
                }

                detections.append(detection)

                # ---------- MEMORY STORAGE ----------
                if self.landmark_memory and drone_position:

                    try:
                        cluster_id = None

                        if self.cluster_memory:
                            cluster = self.cluster_memory.add_detection(
                                normalized_label,
                                drone_position
                            )
                            if cluster:
                                cluster_id = cluster["id"]

                        self.landmark_memory.add_landmark(
                            normalized_label,
                            list(drone_position),
                            yaw=drone_yaw,
                            confidence=confidence,
                            cluster_id=cluster_id
                        )

                    except Exception:
                        pass

        print("Final Detections:", detections)

        return detections