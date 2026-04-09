import numpy as np


class HybridFrontierSelector:

    """
    Hybrid Frontier Selector

    Combines:
    - exploration metrics
    - instruction alignment
    - travel cost
    """

    def __init__(self):

        pass

    # -----------------------------------------------------

    def compute_instruction_alignment(
        self,
        frontier,
        instruction_landmarks,
        landmark_memory
    ):

        if not instruction_landmarks:
            return 0

        score = 0

        frontier_np = np.array(frontier)

        for landmark in instruction_landmarks:

            positions = landmark_memory.get_landmarks(landmark)

            if not positions:
                continue

            distances = []

            for p in positions:

                try:

                    if isinstance(p, dict):
                        pos = p.get("pos")
                    else:
                        pos = p

                    if pos is None:
                        continue

                    pos_np = np.array(pos)

                    d = np.linalg.norm(frontier_np - pos_np)

                    distances.append(d)

                except Exception:
                    continue

            if not distances:
                continue

            nearest = min(distances)

            # prevent divide by zero
            score += 1 / (1 + max(nearest, 0.5))

        return score

    # -----------------------------------------------------

    def compute_travel_cost(self, frontier, current_position):

        if current_position is None:
            return 0

        dist = np.linalg.norm(
            np.array(frontier) - np.array(current_position)
        )

        # normalize cost
        return dist / 50.0

    # -----------------------------------------------------

    def compute_frontier_score(
        self,
        frontier,
        map_metadata,
        instruction_landmarks,
        landmark_memory,
        current_position=None
    ):

        # safer key matching
        key = f"{int(round(frontier[0]))}_{int(round(frontier[1]))}"

        data = map_metadata.get(key, {})

        information_gain = data.get("information_gain", 0)
        entropy = data.get("entropy_score", 0)
        interest = data.get("interest_score", 0)
        collision_penalty = data.get("collision_penalty", 0)

        instruction_score = self.compute_instruction_alignment(
            frontier,
            instruction_landmarks,
            landmark_memory
        )

        travel_cost = self.compute_travel_cost(
            frontier,
            current_position
        )

        score = (
            0.30 * information_gain +
            0.20 * entropy +
            0.20 * interest +
            0.20 * instruction_score -
            0.05 * collision_penalty -
            0.05 * travel_cost
        )

        return score

    # -----------------------------------------------------

    def select_best_frontier(
        self,
        frontiers,
        map_metadata,
        instruction_landmarks,
        landmark_memory,
        current_position=None
    ):

        best_frontier = None
        best_score = -float("inf")

        for frontier in frontiers:

            score = self.compute_frontier_score(
                frontier,
                map_metadata,
                instruction_landmarks,
                landmark_memory,
                current_position
            )

            if score > best_score:

                best_score = score
                best_frontier = frontier

        return best_frontier