import networkx as nx
import math


class SpatialMemoryGraph:

    """
    Spatial Memory Graph for drone navigation.

    Stores explored grid cells and supports:
    - A* path planning
    - Dijkstra exploration
    - BFS nearest search
    """

    def __init__(self):

        self.graph = nx.Graph()

    # -------------------------------------------------

    def add_node(self, x, y):

        grid = 1

        node = (int(round(x/grid) * grid), int(round(y/grid) * grid))

        if node not in self.graph:

            if self.graph.number_of_nodes() > 5000:
                return

            self.graph.add_node(node)

            # automatically connect neighbors
            neighbors = [
                (node[0]+1, node[1]),
                (node[0]-1, node[1]),
                (node[0], node[1]+1),
                (node[0], node[1]-1),

                # diagonal connections
                (node[0]+1, node[1]+1),
                (node[0]-1, node[1]-1),
                (node[0]+1, node[1]-1),
                (node[0]-1, node[1]+1)
            ]

            for n in neighbors:

                if n in self.graph:

                    self.graph.add_edge(node, n, weight=1)

    # -------------------------------------------------

    def heuristic(self, a, b):

        # Euclidean distance
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    # -------------------------------------------------

    def nearest_node(self, position):

        """
        Snap position to nearest graph node
        """

        if self.graph.number_of_nodes() == 0:
            return None

        best = None
        best_dist = float("inf")

        threshold = 1.5

        for node in self.graph.nodes:

            dist = math.sqrt(
                (node[0] - position[0])**2 +
                (node[1] - position[1])**2
            )

            if dist < best_dist:

                best_dist = dist
                best = node

                if best_dist < threshold:
                    break

        return best

    # -------------------------------------------------

    def astar_path(self, start, goal):

        start_node = self.nearest_node(start)
        goal_node = self.nearest_node(goal)

        if start_node is None or goal_node is None:
            return None

        try:

            return nx.astar_path(
                self.graph,
                start_node,
                goal_node,
                heuristic=self.heuristic,
                weight="weight"
            )

        except nx.NetworkXNoPath:

            # fallback to BFS search
            try:
                return nx.shortest_path(self.graph, start_node, goal_node)
            
            except:
                return None

    # -------------------------------------------------

    def dijkstra_path(self, start, goal):

        start_node = self.nearest_node(start)
        goal_node = self.nearest_node(goal)

        if start_node is None or goal_node is None:
            return None

        try:

            return nx.dijkstra_path(
                self.graph,
                start_node,
                goal_node,
                weight="weight"
            )

        except nx.NetworkXNoPath:

            return None

    # -------------------------------------------------

    def bfs_nearest(self, start, targets):

        start_node = self.nearest_node(start)

        if start_node is None:
            return None

        visited = set([start_node])

        queue = [(start_node, [start_node])]

        targets = set(targets)

        while queue:

            current, path = queue.pop(0)

            if current in targets:

                return path

            for neighbor in self.graph.neighbors(current):

                if neighbor not in visited:

                    visited.add(neighbor)

                    queue.append((neighbor, path + [neighbor]))

        return None

    # -------------------------------------------------

    def node_count(self):

        return self.graph.number_of_nodes()

    # -------------------------------------------------

    def edge_count(self):

        return self.graph.number_of_edges()