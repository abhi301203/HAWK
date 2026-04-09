import os
import json
import numpy as np

from sentence_transformers import SentenceTransformer


class PathMemoryEngine:

    """
    Hybrid Path Memory Engine

    Stores successful navigation paths linked to instructions.

    Uses semantic similarity to retrieve reusable paths.
    """

    def __init__(
        self,
        memory_dir="data/path_memory",
        similarity_threshold=0.75
    ):

        self.memory_dir = memory_dir
        self.similarity_threshold = similarity_threshold

        os.makedirs(self.memory_dir, exist_ok=True)

        self.paths_file = os.path.join(self.memory_dir, "paths.json")
        self.embeddings_file = os.path.join(self.memory_dir, "embeddings.npy")

        # self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.model = None

        self.paths = []
        self.embeddings = None

        self.load_memory()

    # --------------------------------------------------

    def load_memory(self):

        if os.path.exists(self.paths_file):

            with open(self.paths_file, "r") as f:
                self.paths = json.load(f)

        else:

            self.paths = []

        if os.path.exists(self.embeddings_file):

            self.embeddings = np.load(self.embeddings_file)

        else:

            self.embeddings = np.empty((0, 384), dtype="float32")

        if len(self.paths) != len(self.embeddings):

            print("Warning: path/embedding mismatch. Resetting embeddings.")

            self.embeddings = np.empty((0, 384),dtype="float32")

    # --------------------------------------------------

    def save_memory(self):

        with open(self.paths_file, "w") as f:

            json.dump(self.paths, f, indent=4)

        np.save(self.embeddings_file, self.embeddings)

    # --------------------------------------------------

    def add_path(self, instruction, path, start_position=None, target=None, success=True):

        """
        Store a navigation path linked to an instruction
        """

        if not success or path is None or len(path) == 0:
            return
        
        model = self.get_model()

        embedding = model.encode([instruction])[0]

        # prevent duplicate paths
        if len(self.embeddings) > 0:

            sims = np.dot(self.embeddings, embedding)

            if np.max(sims) > 0.95:
                return

        embedding = embedding / np.linalg.norm(embedding)

        record = {
            "instruction": instruction,
            "start": start_position,
            "target": target,
            "path": path
        }

        # limit memory size
        if len(self.paths) > 2000:

            self.paths.pop(0)
            self.embeddings = self.embeddings[1:]

        self.paths.append(record)

        if self.embeddings.size == 0:

            self.embeddings = np.array([embedding])

        else:

            self.embeddings = np.vstack([self.embeddings, embedding])

        self.save_memory()

    # --------------------------------------------------

    def cosine_similarity(self, a, b):

        dot = np.dot(a, b)

        norm = np.linalg.norm(a) * np.linalg.norm(b)

        if norm == 0:
            return 0

        return dot / norm
    
    # --------------------------------------------------

    def get_model(self):

        if self.model is None:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")

        return self.model

    # --------------------------------------------------

    def search_path(self, instruction):

        if self.embeddings is None or len(self.embeddings) == 0:
            return None
        
        model = self.get_model()

        query_embedding = model.encode([instruction])[0]

        query_embedding = query_embedding / np.linalg.norm(query_embedding)

        best_score = -1
        best_index = None

        for i in range(len(self.embeddings)):

            emb = self.embeddings[i]

            score = self.cosine_similarity(query_embedding, emb)

            if score > best_score:

                best_score = score
                best_index = i

        print(f"Best path similarity score: {best_score:.2f}")

        if best_index is not None and best_score >= self.similarity_threshold:

            record = self.paths[best_index]

            # optional start position validation
            if record.get("start") is not None:
                
                print("\nPath memory reused for instruction")

            return record

        return None


# --------------------------------------------------

if __name__ == "__main__":

    engine = PathMemoryEngine()

    example_path = [
        [0, 0],
        [1, 0],
        [2, 1],
        [3, 2]
    ]

    engine.add_path(
        "go to the building near the road",
        example_path,
        start_position=[0,0],
        target="building"
    )

    result = engine.search_path(
        "move toward the tower near the street"
    )

    print("\nMatched Path:\n")

    print(result)