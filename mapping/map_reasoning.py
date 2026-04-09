class MapReasoner:

    def __init__(self, map_metadata):

        self.map = map_metadata

    def safe_cells(self):

        safe = []

        for key, cell in self.map["cells"].items():

            if cell.get("collision_penalty", 0) < 1:
                safe.append(key)

        return safe

    def interesting_cells(self):

        interesting = []

        for key, cell in self.map["cells"].items():

            if cell.get("information_gain", 0) > 0:
                interesting.append(key)

        return interesting