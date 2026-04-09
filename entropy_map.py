class EntropyMap:

    def __init__(self, visit_map_manager):

        self.visit_map_manager = visit_map_manager

    # ----------------------------------

    def cell_entropy(self, x, y):

        visit_map = self.visit_map_manager.visit_map

        key = f"{x}_{y}"

        visits = visit_map.get(key, 0)

        entropy = 1 / (1 + visits)

        return entropy

    # ----------------------------------

    def cluster_entropy(self, cluster):

        total = 0

        for cx, cy in cluster:

            total += self.cell_entropy(cx, cy)

        return total / max(len(cluster),1)