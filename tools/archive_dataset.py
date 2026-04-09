import os
import shutil
import json


class DatasetArchiver:

    def __init__(self):

        self.data_root = "data"
        self.dataset_root = "datasets/phase1_v1"

        # read domain from config.json automatically
        with open("config.json") as f:
            config = json.load(f)

        self.domain = config["domain_name"]

    # -----------------------------------------------------

    def archive(self):

        print("Archiving dataset for domain:", self.domain)

        target_domain_folder = os.path.join(
            self.dataset_root,
            f"domain_{self.domain}"
        )

        os.makedirs(target_domain_folder, exist_ok=True)

        folders_to_copy = [
            f"raw_images/{self.domain}",  # images
            "collision_logs",
            "map_metadata",
            "visit_map",
            "run_logs"
        ]

        for folder in folders_to_copy:

            source = os.path.join(self.data_root, folder)

            if not os.path.exists(source):
                print("Skipping missing:", source)
                continue

            destination = os.path.join(
                target_domain_folder,
                os.path.basename(folder)
            )

            if os.path.exists(destination):

                print("Updating existing folder:", destination)

                shutil.copytree(
                    source,
                    destination,
                    dirs_exist_ok=True
                )

            else:

                print("Copying:", source)

                shutil.copytree(source, destination)

        print("Archive complete.")