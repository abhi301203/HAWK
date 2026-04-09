import json
import os
import math


class VisitMapManager:

    def __init__(self, grid_resolution=4):

        self.grid_resolution = grid_resolution

        self.penalty_factor = 2.0

        self.metrics = None

        self.map_file = "data/visit_map/visit_map.json"

        os.makedirs("data/visit_map", exist_ok=True)

        if os.path.exists(self.map_file):

            try:
                with open(self.map_file, "r") as f:
                    self.visit_map = json.load(f)

            except:
                self.visit_map = {}

        else:

            self.visit_map = {}

    def set_metrics_logger(self, metrics_logger):

        self.metrics = metrics_logger

    # -------------------------------
    # Convert world coordinates to grid cell
    # -------------------------------

    def get_cell(self, x, y):

        gx = int(round(x / self.grid_resolution))
        gy = int(round(y / self.grid_resolution))

        return f"{gx}_{gy}"

    # -------------------------------
    # Mark visited cell
    # -------------------------------

    def mark_visited(self, x, y):

        cell = self.get_cell(x, y)

        #check if this is a new cell
        is_new_cell = cell not in self.visit_map

        if is_new_cell:
            self.visit_map[cell] = 0
        
        self.visit_map[cell] += 1

        if is_new_cell and self.metrics is not None:
            try:
                self.metrics.new_cells_discovered += 1
            except:
                pass

    # -------------------------------
    # Check if visited
    # -------------------------------

    def is_visited(self, x, y):

        cell = self.get_cell(x, y)

        return cell in self.visit_map

    # -------------------------------
    # Return visit count
    # -------------------------------

    def visit_count(self, x, y):

        cell = self.get_cell(x, y)

        return self.visit_map.get(cell, 0)

    # -------------------------------
    # Save map
    # -------------------------------

    def save(self):

        os.makedirs("data/visit_map", exist_ok=True)

        with open(self.map_file, "w") as f:
            json.dump(self.visit_map, f, indent=4)

    # -------------------------------
    # Coverage statistics
    # -------------------------------

    def coverage_stats(self):

        total_cells = len(self.visit_map)

        visit_values = list(self.visit_map.values())

        revisits = sum([1 for v in visit_values if v > 1])

        stats = {

            "total_visited_cells": total_cells,

            "revisited_cells": revisits,

            "max_visit_count": max(visit_values) if visit_values else 0
        }

        return stats


    # -------------------------------
    # Visit Penalty
    # -------------------------------
    def visit_penalty(self, x, y):

        count = self.visit_count(x, y)

        return count * self.penalty_factor

    # -------------------------------
    # Frontier search
    # -------------------------------

    # def find_frontier(self, x, y, search_radius=10):

    #     gx = int(math.floor(x / self.grid_resolution))
    #     gy = int(math.floor(y / self.grid_resolution))

    #     for r in range(1, search_radius + 1):

    #         for dx in range(-r, r + 1):

    #             for dy in range(-r, r + 1):

    #                 cell = f"{gx + dx}_{gy + dy}"

    #                 if cell not in self.visit_map:

    #                     target_x = (gx + dx) * self.grid_resolution
    #                     target_y = (gy + dy) * self.grid_resolution

    #                     return target_x, target_y

    #     return None