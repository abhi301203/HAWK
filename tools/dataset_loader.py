import os
import json


class HawkDatasetLoader:

    def __init__(self, dataset_path):

        self.dataset_path = dataset_path

        index_file = os.path.join(dataset_path, "dataset_index.json")

        with open(index_file, "r") as f:
            self.index = json.load(f)

        self.images_root = os.path.join(
            dataset_path,
            self.index["paths"]["images_root"]
        )

    def get_runs(self):

        runs = []

        if not os.path.exists(self.images_root):
            return runs

        for folder in os.listdir(self.images_root):

            path = os.path.join(self.images_root, folder)

            if os.path.isdir(path):
                runs.append(path)

        return runs

    def load_images_with_metadata(self):

        dataset = []

        for run_path in self.get_runs():

            metadata_path = os.path.join(
                run_path,
                self.index["metadata_file"]
            )

            if not os.path.exists(metadata_path):
                continue

            try:
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
            except:
                continue

            for item in metadata:

                image_name = item.get("image_name")

                if not image_name:
                    continue

                image_path = os.path.join(run_path, image_name)

                # -------- SAFE FIELD EXTRACTION --------

                x = item.get("x", 0)
                y = item.get("y", 0)
                z = item.get("z", 0)

                yaw = item.get("yaw_actual")
                if yaw is None:
                    yaw = item.get("yaw_command", 0)

                dataset.append({
                    "image": image_path,
                    "x": x,
                    "y": y,
                    "z": z,
                    "yaw": yaw,
                    "metadata": item   # keep full metadata for future features
                })

        return dataset

    def get_map_metadata(self):

        path = os.path.join(
            self.dataset_path,
            self.index["paths"]["map_metadata"]
        )

        if not os.path.exists(path):
            return None

        with open(path, "r") as f:
            return json.load(f)