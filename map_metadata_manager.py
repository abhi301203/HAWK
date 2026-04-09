import json
import os
import math


class MapMetadataManager:

    def __init__(self, visit_map_manager, collision_memory, capture_manager):

        self.visit_map_manager = visit_map_manager
        self.collision_memory = collision_memory
        self.capture_manager = capture_manager

        self.grid_resolution = visit_map_manager.grid_resolution

        self.file_path = "data/map_metadata/map_metadata.json"

        if not os.path.exists("data/map_metadata"):
            os.makedirs("data/map_metadata")

        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {"cells": {}}

    # --------------------------------------------------

    def update_cell(self, x, y):

        gx = int(round(x / self.grid_resolution))
        gy = int(round(y / self.grid_resolution))

        key = f"{gx}_{gy}"

        visit_map = self.visit_map_manager.visit_map
        visit_count = visit_map.get(key, 0)

        near_obstacle = False
        collision_penalty = 0

        for ox, oy in self.collision_memory.data:

            dx = gx * self.grid_resolution - ox
            dy = gy * self.grid_resolution - oy

            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 8:
                near_obstacle = True
                collision_penalty += (8 - dist)

        if key not in self.data["cells"]:
            self.data["cells"][key] = {}

        cell = self.data["cells"][key]

        cell["visit_count"] = visit_count

        # ---------- EXPLORATION METRICS ----------

        entropy_score = getattr(self.visit_map_manager, "last_entropy", 0)
        interest_score = getattr(self.visit_map_manager, "last_interest", 0)
        heat_value = visit_count

        information_gain = getattr(self.visit_map_manager, "last_information_gain", 0)

        cell["entropy_score"] = float(entropy_score)
        cell["interest_score"] = float(interest_score)
        cell["heat_value"] = int(heat_value)
        cell["information_gain"] = float(information_gain)
        cell["near_obstacle"] = near_obstacle
        cell["collision_penalty"] = collision_penalty

        # ensure required fields exist
        if "images" not in cell:
            cell["images"] = []

        if "altitudes" not in cell:
            cell["altitudes"] = []

        if "yaws" not in cell:
            cell["yaws"] = []

        if "image_count" not in cell:
            cell["image_count"] = 0

        if "exploration_success" not in cell:
            cell["exploration_success"] = 0

    # --------------------------------------------------

    def update_images(self, x, y, image_ids, altitude=None, yaw_list=None):

        gx = int(round(x / self.grid_resolution))
        gy = int(round(y / self.grid_resolution))

        key = f"{gx}_{gy}"

        if key not in self.data["cells"]:
            self.data["cells"][key] = {
                "visit_count": 0,
                "near_obstacle": False,
                "collision_penalty": 0,
                "images": [],
                "altitudes": [],
                "yaws": []
            }

        cell = self.data["cells"][key]

        # ensure fields exist (important for old metadata)
        if "images" not in cell:
            cell["images"] = []

        if "altitudes" not in cell:
            cell["altitudes"] = []

        if "yaws" not in cell:
            cell["yaws"] = []

        # store images
        if image_ids:
            for img in image_ids:
                if img not in cell["images"]:
                    cell["images"].append(img)

        # update image count
        cell["image_count"] = len(cell["images"])

        # store altitude
        if altitude is not None:
            cell["altitudes"].append(float(altitude))

        # store yaw views
        if yaw_list is not None:
            for yaw in yaw_list:
                if yaw not in cell["yaws"]:
                    cell["yaws"].append(yaw)

    # --------------------------------------------------

    def save(self):

        with open(self.file_path, "w") as f:
            json.dump(self.data, f, indent=4)










# import json
# import os
# import math


# class MapMetadataManager:

#     def __init__(self, visit_map_manager, collision_memory, capture_manager):

#         self.visit_map_manager = visit_map_manager
#         self.collision_memory = collision_memory
#         self.capture_manager = capture_manager

#         self.file_path = "data/map_metadata/map_metadata.json"

#         if not os.path.exists("data/map_metadata"):
#             os.makedirs("data/map_metadata")

#         if os.path.exists(self.file_path):
#             with open(self.file_path, "r") as f:
#                 self.data = json.load(f)
#         else:
#             self.data = {"cells": {}}

#     # --------------------------------------------------

#     def update_cell(self, x, y):

#         gx = int(round(x / self.visit_map_manager.grid_resolution))
#         gy = int(round(y / self.visit_map_manager.grid_resolution))

#         key = f"{gx}_{gy}"

#         visit_map = self.visit_map_manager.visit_map

#         visit_count = visit_map.get(key, 0)

#         near_obstacle = False
#         collision_penalty = 0

#         for ox, oy in self.collision_memory.data:

#             dx = gx * self.visit_map_manager.grid_resolution - ox
#             dy = gy * self.visit_map_manager.grid_resolution - oy

#             dist = math.sqrt(dx * dx + dy * dy)

#             if dist < 8:
#                 near_obstacle = True
#                 collision_penalty += (8 - dist)

#         images = []

#         if hasattr(self.capture_manager, "last_capture_ids"):
#             images = self.capture_manager.last_capture_ids

#         self.data["cells"][key] = {

#             "visit_count": visit_count,
#             "near_obstacle": near_obstacle,
#             "collision_penalty": collision_penalty,
#             "images": images

#         }

#     # --------------------------------------------------

#     def update_images(self, x, y, image_ids, altitude=None, yaw_list=None):

#         key = f"{round(x)}_{round(y)}"

#         if key not in self.metadata["cells"]:
#             return

#         cell = self.metadata["cells"][key]

#         # images
#         if "images" not in cell:
#             cell["images"] = []

#         for img in image_ids:
#             if img not in cell["images"]:
#                 cell["images"].append(img)

#         # altitude info
#         if altitude is not None:
#             if "altitudes" not in cell:
#                 cell["altitudes"] = []
#             if altitude not in cell["altitudes"]:
#                 cell["altitudes"].append(altitude)

#         # yaw directions
#         if yaw_list is not None:
#             if "yaw_views" not in cell:
#                 cell["yaw_views"] = []

#             for y in yaw_list:
#                 if y not in cell["yaw_views"]:
#                     cell["yaw_views"].append(y)

#     # --------------------------------------------------

#     def update_images(self, x, y, image_ids, altitude=None, yaw_list=None):

#         gx = int(x / self.grid_resolution)
#         gy = int(y / self.grid_resolution)

#         cell_key = f"{gx}_{gy}"

#         if cell_key not in self.metadata["cells"]:
#             self.metadata["cells"][cell_key] = {
#                 "visit_count": 0,
#                 "near_obstacle": False,
#                 "collision_penalty": 0,
#                 "images": [],
#                 "altitudes": [],
#                 "yaws": []
#             }

#         cell = self.metadata["cells"][cell_key]

#         # store images
#         if image_ids:
#             cell["images"].extend(image_ids)

#         # store altitude
#         if altitude is not None:
#             cell["altitudes"].append(float(altitude))

#         # store yaw directions
#         if yaw_list is not None:
#             cell["yaws"].extend(yaw_list)

#     # --------------------------------------------------

#     def save(self):

#         with open(self.file_path, "w") as f:
#             json.dump(self.data, f, indent=4)