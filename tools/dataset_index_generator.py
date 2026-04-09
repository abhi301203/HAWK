import os
import json
from datetime import datetime


class DatasetIndexGenerator:

    def __init__(self, dataset_path, domain):

        self.dataset_path = dataset_path
        self.domain = domain

    def generate(self):

        # detect image folder automatically
        images_root = None

        for item in os.listdir(self.dataset_path):

            if item.startswith(self.domain.split("_")[0]):
                images_root = item

        if images_root is None:
            images_root = self.domain

        index = {

            "domain": self.domain,

            "created_on": datetime.now().isoformat(),

            "paths": {

                "images_root": images_root,

                "visit_maps": "visit_map",

                "collision_logs": "collision_logs",

                "map_metadata": "map_metadata/map_metadata.json",

                "run_logs": "run_logs"

            },

            "image_format": "png",

            "metadata_file": "metadata.json"
        }

        index_path = os.path.join(self.dataset_path, "dataset_index.json")

        with open(index_path, "w") as f:
            json.dump(index, f, indent=4)

        print("Dataset index generated:", index_path)