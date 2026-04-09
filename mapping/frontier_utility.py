import math


class FrontierUtility:

    def __init__(self, visit_map_manager, collision_memory=None):

        self.visit_map_manager = visit_map_manager
        self.grid_resolution = visit_map_manager.grid_resolution
        self.collision_memory = collision_memory

        # weight parameters
        self.w_gain = 2.0
        self.w_distance = 1.0
        self.w_visit = 1.5
        self.w_expand = 0.8
        self.w_collision = 3.0


    # --------------------------------------------------

    def information_gain(self, fx, fy):

        """
        Estimate unexplored space around frontier.
        Larger neighborhood improves exploration decisions.
        """

        visit_map = self.visit_map_manager.visit_map

        gain = 0

        # 8-neighborhood instead of 4
        neighbors = [
            (fx + 1, fy),
            (fx - 1, fy),
            (fx, fy + 1),
            (fx, fy - 1),
            (fx + 1, fy + 1),
            (fx - 1, fy - 1),
            (fx + 1, fy - 1),
            (fx - 1, fy + 1)
        ]

        for nx, ny in neighbors:

            key = f"{nx}_{ny}"

            if key not in visit_map:
                gain += 1

        return gain


    # --------------------------------------------------

    def visit_penalty(self, fx, fy):

        """
        Penalize frontiers near heavily explored regions
        """

        visit_map = self.visit_map_manager.visit_map

        penalty = 0

        neighbors = [
            (fx + 1, fy),
            (fx - 1, fy),
            (fx, fy + 1),
            (fx, fy - 1)
        ]

        for nx, ny in neighbors:

            key = f"{nx}_{ny}"

            if key in visit_map:
                penalty += visit_map[key]

        return penalty


# --------------------------------------------------

    def collision_penalty(self, fx, fy):

        """
        Penalize frontiers near known collision zones
        """

        if self.collision_memory is None:
            return 0

        penalty = 0

        collision_points = self.collision_memory.data

        for cx, cy in collision_points:

            dx = fx * self.grid_resolution - cx
            dy = fy * self.grid_resolution - cy

            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 8:   # repulsion radius (meters)
                penalty += (8 - dist)

        return penalty

    # --------------------------------------------------

    def expansion_bias(self, fx, fy):

        """
        Encourage exploration outward from explored center
        This creates bubble-style expansion instead of zig-zag motion
        """

        visit_map = self.visit_map_manager.visit_map

        if not visit_map:
            return 0

        xs = []
        ys = []

        for cell in visit_map.keys():

            gx, gy = map(int, cell.split("_"))

            xs.append(gx)
            ys.append(gy)

        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)

        distance_from_center = math.sqrt(
            (fx - center_x) ** 2 +
            (fy - center_y) ** 2
        )

        return distance_from_center


    # --------------------------------------------------

    def compute_utility(self, drone_x, drone_y, frontiers):

        if not frontiers:
            return None

        visit_map = self.visit_map_manager.visit_map

        gx = int(round(drone_x / self.grid_resolution))
        gy = int(round(drone_y / self.grid_resolution))

        # ---- compute map center once ----
        if visit_map:

            xs = []
            ys = []

            for cell in visit_map.keys():
                cx, cy = map(int, cell.split("_"))
                xs.append(cx)
                ys.append(cy)

            center_x = sum(xs) / len(xs)
            center_y = sum(ys) / len(ys)

        else:
            center_x = gx
            center_y = gy

        best_frontier = None
        best_score = -float("inf")

        for fx, fy in frontiers:

            gain = self.information_gain(fx, fy)

            try:
                self.visit_map_manager.metrics.information_gain_total += gain
            except:
                pass

            distance = math.sqrt((fx - gx) ** 2 + (fy - gy) ** 2)

            visit_cost = self.visit_penalty(fx, fy)

            # expansion bias
            expansion = math.sqrt((fx - center_x) ** 2 + (fy - center_y) ** 2)

            collision_cost = self.collision_penalty(fx, fy)

            score = (
                self.w_gain * gain
                - self.w_distance * distance
                - self.w_visit * visit_cost
                - self.w_collision * collision_cost
                + self.w_expand * expansion
            )

            try:
                self.visit_map_manager.metrics.exploration_score_total += score
            except:
                pass

            if score > best_score:

                best_score = score
                best_frontier = (fx, fy)

        if best_frontier is None:
            return None

        wx = best_frontier[0] * self.grid_resolution
        wy = best_frontier[1] * self.grid_resolution

        return wx, wy