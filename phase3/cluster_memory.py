import os
import json
import time
import numpy as np


class ClusterMemory:

    """
    Stores spatial clusters of detected objects.

    Used by:
    - exploration mode
    - VLN navigation
    - semantic reasoning
    """

    def __init__(self, memory_dir="data/cluster_memory", radius=15):

        self.memory_dir = memory_dir
        self.cluster_radius = radius

        os.makedirs(self.memory_dir, exist_ok=True)

        self.cache = {}

    # -------------------------------------------------

    def _get_file(self, label):

        return os.path.join(self.memory_dir, f"{label}_clusters.json")

    # -------------------------------------------------

    def _load_clusters(self, label):

        if label in self.cache:
            return self.cache[label]

        file_path = self._get_file(label)

        if os.path.exists(file_path):

            with open(file_path, "r") as f:
                data = json.load(f)

        else:

            data = {"clusters": []}

        self.cache[label] = data

        return data

    # -------------------------------------------------

    def _save_clusters(self, label):

        data = self.cache[label]

        file_path = self._get_file(label)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    # -------------------------------------------------

    def _distance(self, a, b):

        return np.linalg.norm(np.array(a) - np.array(b))

    # -------------------------------------------------

    def add_detection(self, label, position):

        """
        Add detected object position to cluster memory
        """

        clusters_data = self._load_clusters(label)

        clusters = clusters_data["clusters"]

        position = list(position)

        # search nearest cluster
        best_cluster = None
        best_dist = float("inf")

        for c in clusters:

            centroid = c["centroid"]

            d = self._distance(position, centroid)

            if d < best_dist:

                best_dist = d
                best_cluster = c

        # assign to existing cluster
        if best_cluster and best_dist < self.cluster_radius:

            best_cluster["points"].append(position)

            best_cluster["visits"] += 1

            best_cluster["last_seen"] = time.time()

            # update centroid
            pts = np.array(best_cluster["points"])

            best_cluster["centroid"] = pts.mean(axis=0).tolist()

            best_cluster["confidence"] = min(
                1.0,
                best_cluster["visits"] / 10
            )

        else:

            # create new cluster

            new_cluster = {

                "id": len(clusters) + 1,
                "centroid": position,
                "points": [position],
                "visits": 1,
                "confidence": 0.1,
                "last_seen": time.time()

            }

            clusters.append(new_cluster)

        self._save_clusters(label)

    # -------------------------------------------------

    def get_clusters(self, label):

        data = self._load_clusters(label)

        return data["clusters"]

    # -------------------------------------------------

    def get_best_cluster(self, label, current_position):

        """
        Returns best cluster to search
        """

        clusters = self.get_clusters(label)

        if not clusters:
            return None

        best_cluster = None
        best_score = -float("inf")

        for c in clusters:

            centroid = c["centroid"]

            dist = self._distance(current_position, centroid)

            confidence = c["confidence"]

            score = confidence - (0.01 * dist)

            if score > best_score:

                best_score = score
                best_cluster = c

        return best_cluster