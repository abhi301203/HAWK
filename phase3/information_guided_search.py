import random
import numpy as np
import math


class InformationGuidedSearch:

    """
    Smart search module used when target object
    is not immediately visible.

    Search is guided by:
    - map exploration data
    - distance preference
    - visit frequency
    - optional object memory hints
    """

    def __init__(self, search_radius=40):

        self.search_radius = search_radius

    # --------------------------------------------------

    def extract_position(self, key, cell):

        """
        Support both position formats
        """

        pos = cell.get("position")

        if pos is not None:
            return pos

        try:
            x, y = key.split("_")
            return [int(x), int(y)]
        except Exception:
            return None

    # --------------------------------------------------

    def compute_score(
        self,
        cell,
        position,
        current_position
    ):

        visit_count = cell.get("visit_count", 0)

        information_gain = cell.get("information_gain", 0)

        entropy = cell.get("entropy_score", 0)

        interest = cell.get("interest_score", 0)

        collision_penalty = cell.get("collision_penalty", 0)

        dist = np.linalg.norm(
            np.array(position) - np.array(current_position)
        )

        # prefer moderate distance targets
        distance_bonus = dist * 0.05

        score = (
            0.35 * information_gain +
            0.20 * entropy +
            0.20 * interest +
            0.15 * (1 / (1 + visit_count)) +
            distance_bonus -
            0.15 * collision_penalty
        )

        return score

    # --------------------------------------------------

    def select_search_target(
        self,
        current_position,
        map_metadata,
        object_memory=None
    ):

        cells = map_metadata

        if not cells:
            return self.random_search(current_position)

        candidates = []

        for key, cell in cells.items():

            pos = self.extract_position(key, cell)

            if pos is None:
                continue

            dist = np.linalg.norm(
                np.array(pos) - np.array(current_position)
            )

            if dist > self.search_radius:
                continue

            score = self.compute_score(
                cell,
                pos,
                current_position
            )

            candidates.append((score, pos))

        if len(candidates) == 0:
            return self.random_search(current_position)

        candidates.sort(reverse=True)

        return candidates[0][1]

    # --------------------------------------------------

    def random_search(self, current_position):

        """
        Controlled radial search
        """

        angle = random.uniform(0, 2 * math.pi)

        radius = random.uniform(10, 25)

        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)

        return (
            current_position[0] + dx,
            current_position[1] + dy
        )