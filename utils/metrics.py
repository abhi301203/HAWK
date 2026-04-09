import os
import json
from datetime import datetime


class MetricsLogger:

    def __init__(self, domain):

        self.domain = domain

        # ---------------- CORE METRICS ----------------

        self.images_captured = 0
        self.collisions = 0
        self.successful_escapes = 0
        self.distance_travelled = 0.0

        # ---------------- EXPLORATION METRICS ----------------

        self.grid_attempted = 0
        self.grid_completed = 0
        self.grid_blocked = 0

        # ---------------- MOVEMENT METRICS ----------------

        self.total_yaw_rotations = 0
        self.direction_switches = 0
        self.rows_completed = 0

        # ---------------- SAFETY METRICS ----------------

        self.stuck_events = 0
        self.forced_relocations = 0

        # ---------------- DATA PATHS ----------------

        os.makedirs("data/run_logs", exist_ok=True)

        # ---------------- EXPLORATION METRICS ----------------

        self.frontier_targets_selected = 0
        self.frontiers_rejected = 0
        self.frontier_distance_total = 0
        self.information_gain_total = 0
        self.exploration_score_total = 0

        # ---------------- MAP EXPANSION ----------------

        self.new_cells_discovered = 0
        self.map_expansion_rate = 0
        self.unknown_cells_remaining = 0

        # ---------------- COLLISION / REPULSION ----------------

        self.collision_zones_created = 0
        self.repulsion_events = 0
        self.frontier_blocked_by_collision = 0

        # ---------------- DECISION METRICS ----------------

        self.decision_count = 0
        self.utility_score_total = 0
        self.avg_decision_time = 0

        # ---------------- VLN PREPARATION ----------------

        self.instruction_queries = 0
        self.instruction_success = 0
        self.semantic_targets_found = 0

    # -----------------------------------------------------

    def compute(self, runtime):

        runtime_minutes = runtime / 60

        coverage = 0
        if self.grid_attempted > 0:
            coverage = (self.grid_completed / self.grid_attempted) * 100

        images_per_minute = 0
        if runtime_minutes > 0:
            images_per_minute = self.images_captured / runtime_minutes

        distance_per_minute = 0
        if runtime_minutes > 0:
            distance_per_minute = self.distance_travelled / runtime_minutes

        collision_rate = 0
        if runtime_minutes > 0:
            collision_rate = self.collisions / runtime_minutes

        # -------- EXPLORATION METRICS CALCULATION --------

        frontier_efficiency = 0
        if self.frontier_targets_selected > 0:
            frontier_efficiency = (
                self.new_cells_discovered /
                self.frontier_targets_selected
            )

        map_expansion_rate = 0
        if runtime_minutes > 0:
            map_expansion_rate = (
                self.new_cells_discovered /
                runtime_minutes
            )

        # -------- SANITY CHECK FOR REPULSION METRIC --------

        if self.repulsion_events > (self.grid_attempted * 5):
            self.repulsion_events = 0

        # -------- ADDITIONAL DERIVED METRICS --------

        avg_information_gain = 0
        if self.frontier_targets_selected > 0:
            avg_information_gain = (
                self.information_gain_total /
                self.frontier_targets_selected
            )

        avg_distance_per_frontier = 0
        if self.frontier_targets_selected > 0:
            avg_distance_per_frontier = (
                self.frontier_distance_total /
                self.frontier_targets_selected
            )

        # -------- FINAL METRICS DICTIONARY --------

        metrics = {

            # Domain
            "domain": self.domain,

            # Runtime
            "runtime_minutes": round(runtime_minutes, 2),

            # Core
            "images_captured": self.images_captured,
            "collisions": self.collisions,
            "successful_escapes": self.successful_escapes,
            "distance_travelled": round(self.distance_travelled, 2),

            # Grid Exploration
            "total_grid_cells_attempted": self.grid_attempted,
            "grid_cells_completed": self.grid_completed,
            "grid_cells_blocked": self.grid_blocked,
            "coverage_percentage": round(coverage, 2),

            # Movement
            "total_yaw_rotations": self.total_yaw_rotations,
            "number_of_grid_rows_completed": self.rows_completed,
            "number_of_direction_switches": self.direction_switches,

            # Efficiency
            "images_per_minute": round(images_per_minute, 2),
            "distance_per_minute": round(distance_per_minute, 2),
            "collision_rate_per_minute": round(collision_rate, 2),

            # Safety
            "stuck_events_count": self.stuck_events,
            "forced_relocations": self.forced_relocations,

            # -------- NEW EXPLORATION METRICS --------

            "decision_count": self.decision_count,
            "frontier_targets_selected": self.frontier_targets_selected,
            "information_gain_total": self.information_gain_total,
            "new_cells_discovered": self.new_cells_discovered,
            "repulsion_events": self.repulsion_events,

            "frontier_efficiency": round(frontier_efficiency, 3),
            "map_expansion_rate": round(map_expansion_rate, 3),

            "avg_information_gain": round(avg_information_gain, 3),
            "avg_distance_per_frontier": round(avg_distance_per_frontier, 3)

        }

        # ---------------- SAVE RUN LOG ----------------

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        run_file = f"data/run_logs/run_{timestamp}.json"

        with open(run_file, "w") as f:
            json.dump(metrics, f, indent=4)

        return metrics