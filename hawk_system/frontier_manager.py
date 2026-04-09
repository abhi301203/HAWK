import numpy as np


class FrontierManager:

    """
    Smart Frontier Manager

    Used ONLY when:
    - target not found in perception
    - no strong memory match

    Responsibilities:
    - select meaningful frontier
    - avoid random exploration
    - reduce revisits
    - guide search intelligently
    """

    def __init__(self, max_frontiers=150):

        self.max_frontiers = max_frontiers
        self.previous_target = None

    # --------------------------------------------------

    def extract_frontiers(self, map_metadata):

        """
        Extract valid frontier cells
        """

        frontiers = []

        for key, data in map_metadata.items():

            info_gain = data.get("information_gain", 0)
            visit_count = data.get("visit_count", 0)
            success = data.get("exploration_success", 1)

            # ignore useless cells
            if info_gain <= 0:
                continue

            if visit_count > 3:
                continue

            if success == 0:
                continue

            try:
                x, y = key.split("_")
                frontiers.append((int(x), int(y)))
            except:
                continue

        # limit size safely
        if len(frontiers) > self.max_frontiers:

            step = max(1, len(frontiers) // self.max_frontiers)
            frontiers = frontiers[::step]

        return frontiers

    # --------------------------------------------------

    def select_frontier(
        self,
        current_position,
        map_metadata,
        landmark_memory=None,
        target_label=None
    ):

        """
        Select best frontier intelligently
        """

        frontiers = self.extract_frontiers(map_metadata)

        if not frontiers:
            return None

        best = None
        best_score = -float("inf")

        for f in frontiers:

            score = self._score_frontier(
                f,
                current_position,
                map_metadata,
                landmark_memory,
                target_label
            )

            if score > best_score:
                best_score = score
                best = f

        # ---------- oscillation prevention ----------

        if best == self.previous_target:
            return None

        self.previous_target = best

        return best

    # --------------------------------------------------

    def _score_frontier(
        self,
        frontier,
        current_position,
        map_metadata,
        landmark_memory,
        target_label
    ):

        key = f"{frontier[0]}_{frontier[1]}"
        data = map_metadata.get(key, {})

        info_gain = data.get("information_gain", 0)
        entropy = data.get("entropy_score", 0)
        interest = data.get("interest_score", 0)
        collision = data.get("collision_penalty", 0)

        # ---------- distance penalty ----------

        dist = np.linalg.norm(
            np.array(frontier) - np.array(current_position)
        )

        distance_score = 1 / (1 + dist)

        # ---------- memory guidance ----------

        memory_score = 0

        if target_label and landmark_memory:

            entries = landmark_memory.get_landmarks(target_label)

            if entries:

                distances = []

                for e in entries:

                    pos = e["pos"] if isinstance(e, dict) else e

                    d = np.linalg.norm(
                        np.array(frontier) - np.array(pos)
                    )

                    distances.append(d)

                nearest = min(distances)
                memory_score = 1 / (1 + nearest)

        # ---------- final score ----------

        score = (
            0.30 * info_gain +
            0.20 * entropy +
            0.20 * interest +
            0.20 * memory_score +
            0.10 * distance_score -
            0.15 * collision
        )

        return score