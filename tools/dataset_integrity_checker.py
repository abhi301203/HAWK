import os
import cv2
import json


class DatasetIntegrityChecker:

    def __init__(self, dataset_path):

        self.dataset_path = dataset_path

    # -----------------------------------------------------

    def find_image_root(self):

        for item in os.listdir(self.dataset_path):

            path = os.path.join(self.dataset_path, item)

            if os.path.isdir(path) and item not in [
                "collision_logs",
                "map_metadata",
                "visit_map",
                "run_logs"
            ]:
                return path

        return None

    # -----------------------------------------------------

    def check_images(self, run_folder):

        image_files = []

        for f in os.listdir(run_folder):

            if f.lower().endswith(".png") or f.lower().endswith(".jpg"):
                image_files.append(f)

        corrupt = []

        for img in image_files:

            path = os.path.join(run_folder, img)

            try:

                im = cv2.imread(path)

                if im is None:
                    corrupt.append(img)

            except:
                corrupt.append(img)

        return image_files, corrupt

    # -----------------------------------------------------

    def run(self):

        print("Running dataset integrity check...")

        image_root = self.find_image_root()

        if image_root is None:

            print("Image folder not found.")
            return

        total_images = 0
        corrupt_images = 0

        for run in os.listdir(image_root):

            run_path = os.path.join(image_root, run)

            if not os.path.isdir(run_path):
                continue

            imgs, corrupt = self.check_images(run_path)

            total_images += len(imgs)
            corrupt_images += len(corrupt)

            if corrupt:

                print("Corrupt images in", run)
                print(corrupt)

        print("\nSummary")
        print("Total images:", total_images)
        print("Corrupt images:", corrupt_images)

        if corrupt_images == 0:
            print("Dataset looks healthy.")
        else:
            print("Fix corrupted images before training.")