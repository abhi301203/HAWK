from phase3.hybrid_frontier_selector import HybridFrontierSelector
from phase3.information_guided_search import InformationGuidedSearch
import math


class FrontierExplorationController:

    """
    Hybrid Instruction-Guided Frontier Exploration Controller

    Combines:
    - Phase1 exploration frontiers
    - instruction landmarks
    - landmark memory
    - information-guided search fallback
    """

    def __init__(self):

        self.selector = HybridFrontierSelector()
        self.search_module = InformationGuidedSearch()

        # used to prevent oscillation
        self.previous_frontier = None

    # -----------------------------------------------------

    def get_frontiers_from_phase1(self, map_metadata):

        """
        Extract frontier cells from map metadata
        """

        frontiers = []

        for key, value in map_metadata.items():

            information_gain = value.get("information_gain", 0)
            visit_count = value.get("visit_count", 0)

            # ignore useless cells
            if information_gain <= 0:
                continue

            # ignore overly explored cells
            if visit_count > 3:
                continue

            try:

                x, y = key.split("_")

                frontiers.append((int(x), int(y)))

            except Exception:
                continue

        # remove duplicate coordinates
        frontiers = list(set(frontiers))

        return frontiers

    # -----------------------------------------------------

    def reduce_frontier_set(self, frontiers, limit=200):

        """
        Reduce frontier set safely without bias
        """

        if len(frontiers) <= limit:
            return frontiers

        step = max(1, len(frontiers) // limit)

        return frontiers[::step]

    # -----------------------------------------------------

    def frontier_is_repeated(self, frontier):

        """
        Prevent frontier oscillation
        """

        if self.previous_frontier is None:
            return False

        dx = frontier[0] - self.previous_frontier[0]
        dy = frontier[1] - self.previous_frontier[1]

        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 1.0:
            return True

        return False

    # -----------------------------------------------------

    def select_next_frontier(
        self,
        map_metadata,
        instruction_landmarks,
        landmark_memory,
        current_position=None
    ):

        """
        Select best frontier or fallback search target
        """

        frontiers = self.get_frontiers_from_phase1(map_metadata)

        # reduce frontier count safely
        frontiers = self.reduce_frontier_set(frontiers)

        # -------------------------------------------------
        # FRONTIER SELECTION
        # -------------------------------------------------

        if frontiers:

            best_frontier = self.selector.select_best_frontier(
                frontiers,
                map_metadata,
                instruction_landmarks,
                landmark_memory,
                current_position
            )

            if best_frontier is None:
                return None

            # prevent oscillation
            if self.frontier_is_repeated(best_frontier):

                return None

            self.previous_frontier = best_frontier

            return best_frontier

        # -------------------------------------------------
        # FALLBACK → INFORMATION GUIDED SEARCH
        # -------------------------------------------------

        if current_position is not None:

            print("\nNo frontier available → using search mode")

            return self.search_module.select_search_target(
                current_position,
                map_metadata
            )

        return None