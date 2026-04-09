import os
import json
import time
import numpy as np
from sentence_transformers import SentenceTransformer


class InstructionMemory:

    """
    Episodic Memory for Navigation Instructions

    Stores navigation episodes and allows semantic lookup.
    """

    def __init__(self,
                 memory_dir="data/instruction_memory",
                 similarity_threshold=0.65,
                 max_episodes=5000):

        self.memory_dir = memory_dir
        self.similarity_threshold = similarity_threshold
        self.max_episodes = max_episodes

        os.makedirs(memory_dir, exist_ok=True)

        self.memory_file = os.path.join(memory_dir, "episodes.json")

        # self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.model = None

        self.episodes = []

        self.load_memory()

    # -----------------------------------------------------

    def load_memory(self):

        if os.path.exists(self.memory_file):

            with open(self.memory_file, "r") as f:
                self.episodes = json.load(f)

        else:

            self.episodes = []

        # remove very old episodes (older than 30 days)
        current_time = time.time()

        self.episodes = [
            e for e in self.episodes
            if current_time - e["timestamp"] < 30 * 24 * 3600
        ]

    # -----------------------------------------------------

    def save_memory(self):

        with open(self.memory_file, "w") as f:
            json.dump(self.episodes, f, indent=4)

    # ----------------------------------------------------

    def get_model(self):

        if self.model is None:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        return self.model

    # -----------------------------------------------------

    def normalize_path(self, path):

        if path is None:
            return []

        return [list(p) for p in path]

    # -----------------------------------------------------

    def add_episode(
        self,
        instruction,
        path,
        success,
        collisions,
        runtime_minutes
    ):
        
        model = self.get_model()

        embedding = model.encode([instruction][0])

        episode = {
            "timestamp": time.time(),
            "instruction": instruction,
            "path": self.normalize_path(path),
            "success": success,
            "collisions": collisions,
            "runtime_minutes": runtime_minutes
        }

        # ignore bad navigation episodes
        if collisions > 10:
            return

        self.episodes.append(episode)

        # memory cap
        if len(self.episodes) > self.max_episodes:
            self.episodes = self.episodes[-self.max_episodes:]

        self.save_memory()

    # -----------------------------------------------------

    def semantic_match(self, instruction):

        if not self.episodes:
            return []
        
        model = self.get_model()

        query = model.encode([instruction])[0]

        matches = []

        for e in self.episodes:

            emb = np.array(e["embedding"])

            score = np.dot(query, emb) / (
                np.linalg.norm(query) * np.linalg.norm(emb)
            )

            if score >= self.similarity_threshold:
                matches.append(e)

        print(f"Instruction memory matches found: {len(matches)}")

        return matches

    # -----------------------------------------------------

    def get_recent_episodes(self, limit=10):

        return self.episodes[-limit:]

    # -----------------------------------------------------

    def get_success_rate(self, instruction):

        relevant = self.semantic_match(instruction)

        if not relevant:
            return 0

        successes = sum(1 for e in relevant if e["success"])

        if len(relevant) == 0:
            return 0

        return successes / len(relevant)

    # -----------------------------------------------------

    def get_best_episode(self, instruction):

        relevant = self.semantic_match(instruction)

        if not relevant:
            return None

        best = sorted(
            relevant,
            key=lambda x: (
                not x["success"],
                x["collisions"],
                x["runtime_minutes"]
            )
        )

        return best[0]