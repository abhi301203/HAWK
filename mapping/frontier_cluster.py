import math


class FrontierCluster:

    def __init__(self, visit_map_manager, collision_memory=None, entropy_map=None):

        self.visit_map_manager = visit_map_manager
        self.grid_resolution = visit_map_manager.grid_resolution
        self.collision_memory = collision_memory
        self.entropy_map = entropy_map

        self.cluster_radius = 6

        self.previous_cell = None

        self.cluster_failures = {}

    # --------------------------------------------------

    def cluster_frontiers(self, frontiers):

        """
        Group nearby frontier cells into clusters
        """

        clusters = []
        visited = set()

        for fx, fy in frontiers:

            if (fx, fy) in visited:
                continue

            cluster = [(fx, fy)]
            visited.add((fx, fy))

            for ox, oy in frontiers:

                if (ox, oy) in visited:
                    continue

                dist = math.sqrt((fx - ox) ** 2 + (fy - oy) ** 2)

                if dist <= self.cluster_radius:
                    cluster.append((ox, oy))
                    visited.add((ox, oy))

            clusters.append(cluster)

        return clusters


    # --------------------------------------------------

    def cluster_center(self, cluster):

        xs = [c[0] for c in cluster]
        ys = [c[1] for c in cluster]

        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)

        return cx, cy
    
    # --------------------------------------------------
    

    def exploration_pressure(self, cx, cy):

        """
        Encourage clusters far from explored center
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

        dist = math.sqrt(
            (cx - center_x) ** 2 +
            (cy - center_y) ** 2
        )

        return dist
    
    # --------------------------------------------------

    def wave_expansion_bias(self, cx, cy):

        """
        Encourage outward wave exploration 
        """

        visit_map = self.visit_map_manager.visit_map

        if not visit_map:
            return 0
        
        xs = []
        ys = []

        for cell in visit_map:

            gx, gy = map(int, cell.split("_"))

            xs.append(gx)
            ys.append(gy)

        center_x = sum(xs) / len(xs)
        center_y = sum(ys) / len(ys)

        dist = math.sqrt(
            (cx - center_x) ** 2 +
            (cy - center_y) ** 2
        )

        # preferred expansion distance
        optimal = 8

        return -abs(dist - optimal)

    # --------------------------------------------------

    def cluster_information_gain(self, cluster):

        """
        Total unexplored neighbors for cluster
        """

        visit_map = self.visit_map_manager.visit_map
        gain = 0

        for fx, fy in cluster:

            neighbors = [
                (fx + 1, fy),
                (fx - 1, fy),
                (fx, fy + 1),
                (fx, fy - 1)
            ]

            for nx, ny in neighbors:

                key = f"{nx}_{ny}"

                if key not in visit_map:
                    gain += 1

        return gain

    # --------------------------------------------------

    def collision_penalty(self, cx, cy):

        if self.collision_memory is None:
            return 0

        penalty = 0

        for px, py in self.collision_memory.data:

            dx = cx * self.grid_resolution - px
            dy = cy * self.grid_resolution - py

            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 8:
                penalty += (8 - dist)

        return penalty
    
    # --------------------------------------------------  
    #  

    def direction_bias(self, cx, cy, gx, gy):

        """
        Encourage clusters aligned with exploration direction
        """

        if self.previous_cell is None:
            return 0

        px, py = self.previous_cell

        dx1 = cx - px
        dy1 = cy - py

        dx2 = gx - px
        dy2 = gy - py

        dot = dx1 * dx2 + dy1 * dy2

        if dot > 0:
            return 1.5
        
        return 0

    # --------------------------------------------------

    def best_cluster(self, drone_x, drone_y, frontiers):

        """
        Select best exploration cluster
        """

        if not frontiers:
            return None

        clusters = self.cluster_frontiers(frontiers)

        gx = drone_x / self.grid_resolution
        gy = drone_y / self.grid_resolution

        best_cluster = None
        best_score = -float("inf")

        for cluster in clusters:

            cx, cy = self.cluster_center(cluster)

            gain = self.cluster_information_gain(cluster)

            distance = math.sqrt((cx - gx) ** 2 + (cy - gy) ** 2)

            collision_cost = self.collision_penalty(cx, cy)

            visit_penalty = self.visit_density_penalty(cluster)

            expansion = self.exploration_pressure(cx, cy)

            heat = self.exploration_heat(cx, cy)

            interest = self.interest_score(cx, cy)

            wave = self.wave_expansion_bias(cx, cy)

            failure_penalty = self.cluster_failure_penalty(cx, cy)

            direction = self.direction_bias(cx, cy, gx, gy)

            entropy = self.entropy_map.cluster_entropy(cluster)

            score = (
                gain * 4
                + expansion * 2
                + interest * 2
                + entropy * 4
                + wave * 0.8
                - distance
                - collision_cost * 2
                - visit_penalty * 2
                - heat * 1.5
                - failure_penalty 
                + direction 
            )

            if score > best_score:
                best_score = score
                best_cluster = cluster

        return best_cluster
    
    # --------------------------------------------------

    def visit_density_penalty(self, cluster):

        visit_map = self.visit_map_manager.visit_map

        penalty = 0

        for fx, fy in cluster:

            key = f"{fx}_{fy}"

            if key in visit_map:
                penalty += visit_map[key]

        return penalty
    
    # --------------------------------------------------

    def exploration_heat(self, cx, cy):

        """
        Calculate exploration density around cluster center
        """

        visit_map = self.visit_map_manager.visit_map

        heat = 0
        radius = 4

        for cell in visit_map:

            gx, gy = map(int, cell.split("_"))

            dist = math.sqrt((cx - gx)**2 + (cy - gy)**2)

            if dist <= radius:
                heat += visit_map[cell]

        return heat
    
    # --------------------------------------------------

    def interest_score(self, cx, cy):

        """
        Curiosity driven exploration score
        Combines entropy + frontier gain + novelty
        """

        visit_map = self.visit_map_manager.visit_map

        # unexplored neighbor count
        visit_map = self.visit_map_manager.visit_map

        gx = int(cx)
        gy = int(cy)

        unknown_neighbors = 0

        neighbors = [
            (gx+1, gy),
            (gx-1, gy),
            (gx, gy+1),
            (gx, gy-1),
            (gx+1, gy+1),
            (gx-1, gy-1),
            (gx+1, gy-1),
            (gx-1, gy+1)
        ]

        for nx, ny in neighbors:

            key = f"{nx}_{ny}"

            if key not in visit_map:
                unknown_neighbors += 1

        return unknown_neighbors
    
    # --------------------------------------------------

    def cluster_failure_penalty(self, cx, cy):

        """
        Penalize clusters near previous failures
        """

        key = f"{round(cx)}_{round(cy)}"

        if key in self.cluster_failures:

            return self.cluster_failures[key] * 2
        
        return 0
    
    # --------------------------------------------------

    def record_cluster_result(self, cx, cy, new_cells):

        key = f"{round(cx)}_{round(cy)}"

        if new_cells > 0:
            
            # successful exploration -> reset failure count
            self.cluster_failures[key] = 0
        
        else:

            # failed exploration -> increment penalty
            self.cluster_failures[key] = self.cluster_failures.get(key, 0) + 1
