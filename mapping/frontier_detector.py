import math


class FrontierDetector:

    def __init__(self, visit_map_manager):

        # reference to visit map system
        self.visit_map_manager = visit_map_manager

        # grid resolution (meters per cell)
        self.grid_resolution = visit_map_manager.grid_resolution

        # detected frontier cells
        self.frontiers = []

        # safety limit (max grid cells drone can jump)
        self.max_frontier_distance_m = 20

        self.max_frontier_distance = self.max_frontier_distance_m / self.grid_resolution


    # --------------------------------------------------

    def _get_neighbors(self, gx, gy):
        """
        Return 8-connected grid neighbors
        """

        return [
            (gx + 1, gy),
            (gx - 1, gy),
            (gx, gy + 1),
            (gx, gy - 1),

            (gx + 1, gy + 1),
            (gx + 1, gy - 1),
            (gx - 1, gy + 1),
            (gx - 1, gy - 1)
        ]


    # --------------------------------------------------

    def detect_frontiers(self):

        if len(self.visit_map_manager.visit_map) == 0:
            return []

        """
        Detect frontier cells.

        Frontier definition:
        unvisited cell that touches at least one visited cell
        """

        visit_map = self.visit_map_manager.visit_map

        frontier_cells = set()
        checked = set()

        for cell in visit_map.keys():

            gx, gy = map(int, cell.split("_"))

            neighbors = self._get_neighbors(gx, gy)

            for nx, ny in neighbors:

                neighbor_key = f"{nx}_{ny}"

                # candidate frontier = unvisited cell
                if neighbor_key not in visit_map:

                    if neighbor_key in checked:
                        continue

                    # verify it borders explored region
                    second_neighbors = self._get_neighbors(nx, ny)

                    for sx, sy in second_neighbors:

                        check_key = f"{sx}_{sy}"

                        if check_key in visit_map and visit_map[check_key] > 0:

                            frontier_cells.add((nx, ny))
                            checked.add(neighbor_key)
                            break

        self.frontiers = list(frontier_cells)

        return self.frontiers


    # --------------------------------------------------

    def get_frontiers(self):
        """
        Return detected frontier list
        """

        return self.frontiers


    # --------------------------------------------------

    def nearest_frontier(self, x, y):

        """
        Simple nearest frontier (baseline method)
        """

        if not self.frontiers:
            return None

        gx = int(round(x / self.grid_resolution))
        gy = int(round(y / self.grid_resolution))

        best = None
        best_dist = float("inf")

        for fx, fy in self.frontiers:

            dist = math.sqrt((fx - gx) ** 2 + (fy - gy) ** 2)

            if dist > self.max_frontier_distance:
                continue

            if dist < best_dist:
                best_dist = dist
                best = (fx, fy)

        if best is None:
            return None

        wx = best[0] * self.grid_resolution
        wy = best[1] * self.grid_resolution

        return wx, wy


    # --------------------------------------------------

    def best_frontier(self, x, y):

        """
        Choose frontier using Information Gain scoring
        """

        if not self.frontiers:
            return None

        visit_map = self.visit_map_manager.visit_map

        gx = int(round(x / self.grid_resolution))
        gy = int(round(y / self.grid_resolution))

        best = None
        best_score = -float("inf")

        for fx, fy in self.frontiers:

            # distance from drone
            dist = math.sqrt((fx - gx) ** 2 + (fy - gy) ** 2)

            if dist > self.max_frontier_distance:
                continue

            # count unknown neighbors (information gain)
            unknown_count = 0

            neighbors = self._get_neighbors(fx, fy)

            for nx, ny in neighbors:

                key = f"{nx}_{ny}"

                if key not in visit_map:
                    unknown_count += 1

            # scoring function
            score = (unknown_count * 3) - dist

            if score > best_score:

                best_score = score
                best = (fx, fy)

        if best is None:
            return None

        wx = best[0] * self.grid_resolution
        wy = best[1] * self.grid_resolution

        return wx, wy