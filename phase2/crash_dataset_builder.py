import json
import os


class CrashDatasetBuilder:

    def __init__(self, map_metadata_path):

        self.map_metadata_path = map_metadata_path

    def build(self):

        if not os.path.exists(self.map_metadata_path):
            return []

        with open(self.map_metadata_path) as f:
            data = json.load(f)

        important_cells = []

        for key, cell in data["cells"].items():

            score = (
                cell.get("entropy_score", 0) +
                cell.get("information_gain", 0) +
                cell.get("heat_value", 0)
            )

            if score > 0:
                important_cells.append({
                    "cell": key,
                    "score": score
                })

        important_cells = sorted(
            important_cells,
            key=lambda x: x["score"],
            reverse=True
        )

        return important_cells[:50]