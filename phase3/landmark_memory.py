import os
import json
import time
import numpy as np


class LandmarkMemory:

    """
    Landmark Memory

    Stores raw object detections with viewpoint information.

    Landmark structure:

    {
        "car":[
            {
              "pos":[x,y],
              "yaw":90,
              "confidence":0.8,
              "cluster_id":2,
              "timestamp":123456
            }
        ]
    }
    """

    def __init__(self,
                 memory_dir="data/landmark_memory",
                 duplicate_radius=4,
                 max_entries_per_label=200):

        self.memory_dir = memory_dir
        os.makedirs(self.memory_dir, exist_ok=True)

        self.memory_file = os.path.join(
            self.memory_dir,
            "landmarks.json"
        )

        self.duplicate_radius = duplicate_radius
        self.max_entries_per_label = max_entries_per_label

        self.landmarks = {}

        self.load_memory()

    # -----------------------------------------------------

    def load_memory(self):

        if os.path.exists(self.memory_file):

            try:
                with open(self.memory_file, "r") as f:
                    self.landmarks = json.load(f)

            except Exception:
                self.landmarks = {}

        else:
            self.landmarks = {}

    # -----------------------------------------------------

    def save_memory(self):

        try:

            with open(self.memory_file, "w") as f:
                json.dump(self.landmarks, f, indent=4)

        except Exception:
            pass

    # -----------------------------------------------------

    def _distance(self, a, b):

        return np.linalg.norm(
            np.array(a) - np.array(b)
        )

    # -----------------------------------------------------

    def add_landmark(self,
                     label,
                     position,
                     yaw=None,
                     confidence=0.5,
                     cluster_id=None):

        """
        Store landmark detection.

        Updates existing entries if detection
        is near an existing landmark.
        """

        if label not in self.landmarks:

            self.landmarks[label] = []

        entries = self.landmarks[label]

        # Check for nearby existing landmark
        for entry in entries:

            dist = self._distance(entry["pos"], position)

            if dist < self.duplicate_radius:

                # Update confidence
                entry["confidence"] = max(
                    entry["confidence"],
                    confidence
                )

                entry["timestamp"] = time.time()

                if cluster_id is not None:
                    entry["cluster_id"] = cluster_id

                self.save_memory()

                return

        # Add new landmark
        new_entry = {

            "pos": list(position),
            "yaw": yaw,
            "confidence": confidence,
            "cluster_id": cluster_id,
            "timestamp": time.time()

        }

        entries.append(new_entry)

        # Prevent unlimited memory growth
        if len(entries) > self.max_entries_per_label:

            entries.pop(0)

        self.save_memory()

    # -----------------------------------------------------

    def get_landmarks(self, label):

        """
        Return raw landmark entries
        """

        return self.landmarks.get(label, [])

    # -----------------------------------------------------

    def get_positions(self, label):

        """
        Extract only positions
        """

        entries = self.landmarks.get(label, [])

        return [e["pos"] for e in entries]

    # -----------------------------------------------------

    def nearest_landmark(self, label, position):

        """
        Find nearest landmark detection
        """

        entries = self.landmarks.get(label, [])

        if len(entries) == 0:

            return None

        best = None
        best_dist = float("inf")

        for entry in entries:

            dist = self._distance(
                entry["pos"],
                position
            )

            if dist < best_dist:

                best_dist = dist
                best = entry

        return best

    # -----------------------------------------------------

    def best_landmark(self, label):

        """
        Return landmark with highest confidence
        """

        entries = self.landmarks.get(label, [])

        if not entries:

            return None

        return max(
            entries,
            key=lambda x: x["confidence"]
        )


# -----------------------------------------------------
# Test block
# -----------------------------------------------------

if __name__ == "__main__":

    memory = LandmarkMemory()

    memory.add_landmark("car", [10, 5], yaw=90, confidence=0.8)
    memory.add_landmark("car", [12, 6], yaw=45, confidence=0.6)
    memory.add_landmark("car", [11, 7], yaw=60, confidence=0.7)

    print("\nStored Landmarks:")
    print(memory.landmarks)

    print("\nNearest Landmark:")
    print(memory.nearest_landmark("car", [9, 4]))

    print("\nBest Landmark:")
    print(memory.best_landmark("car"))