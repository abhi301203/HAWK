import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

try:
    import faiss
    FAISS_AVAILABLE = True
except:
    FAISS_AVAILABLE = False


class HybridInstructionMemory:

    """
    Scalable instruction memory system.

    Uses:
    - NumPy cosine search (< threshold)
    - FAISS cosine search (>= threshold)
    """

    def __init__(
        self,
        memory_dir="data/instruction_memory",
        threshold=1000,
        similarity_threshold=0.65
    ):

        self.memory_dir = memory_dir
        self.threshold = threshold
        self.similarity_threshold = similarity_threshold

        os.makedirs(self.memory_dir, exist_ok=True)

        self.instructions_file = os.path.join(memory_dir, "instructions.json")
        self.embeddings_file = os.path.join(memory_dir, "embeddings.npy")
        self.faiss_index_file = os.path.join(memory_dir, "faiss.index")

        self.model = None
        self.faiss_index = None  # 🔥 cache

        self.instructions = []
        self.embeddings = np.empty((0, 384), dtype="float32")

        self.load_memory()

    # -----------------------------------------------------

    def get_model(self):
        if self.model is None:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        return self.model

    # -----------------------------------------------------

    def normalize(self, v):
        norm = np.linalg.norm(v)
        return v if norm == 0 else v / norm

    # -----------------------------------------------------

    def load_memory(self):

        if os.path.exists(self.instructions_file):
            try:
                with open(self.instructions_file, "r") as f:
                    self.instructions = json.load(f)
            except:
                self.instructions = []

        if os.path.exists(self.embeddings_file):
            try:
                self.embeddings = np.load(self.embeddings_file).astype("float32")
            except:
                self.embeddings = np.empty((0, 384), dtype="float32")

    # -----------------------------------------------------

    def save_memory(self):

        try:
            with open(self.instructions_file, "w") as f:
                json.dump(self.instructions, f, indent=4)
        except Exception as e:
            print(f"Save error (instructions): {e}")

        try:
            np.save(self.embeddings_file, self.embeddings)
        except Exception as e:
            print(f"Save error (embeddings): {e}")

    # -----------------------------------------------------

    def add_instruction(self, instruction_data):

        text = instruction_data.get("instruction", "")

        if not isinstance(text, str) or len(text.strip()) < 5:
            return

        model = self.get_model()

        emb = model.encode([text])[0].astype("float32")
        emb = self.normalize(emb)

        # ---------- DUPLICATE CHECK ----------

        if self.embeddings.shape[0] > 0:

            sims = np.dot(self.embeddings, emb)
            max_sim = float(np.max(sims))

            if max_sim > 0.95:
                return

        # ---------- MEMORY LIMIT ----------

        if len(self.instructions) >= 5000:
            self.instructions.pop(0)
            self.embeddings = self.embeddings[1:]

        # ---------- STORE ----------

        self.instructions.append(instruction_data)

        if self.embeddings.size == 0:
            self.embeddings = np.array([emb], dtype="float32")
        else:
            self.embeddings = np.vstack([self.embeddings, emb])

        self.save_memory()

        # ---------- FAISS UPDATE ----------

        if FAISS_AVAILABLE and len(self.instructions) >= self.threshold:
            self.build_faiss_index()

    # -----------------------------------------------------

    def build_faiss_index(self):

        if not FAISS_AVAILABLE or self.embeddings.shape[0] == 0:
            return

        try:
            dim = self.embeddings.shape[1]

            # IMPORTANT: normalized embeddings for cosine similarity
            normalized = np.array(
                [self.normalize(e) for e in self.embeddings],
                dtype="float32"
            )

            index = faiss.IndexFlatIP(dim)
            index.add(normalized)

            faiss.write_index(index, self.faiss_index_file)

            self.faiss_index = index  # cache

        except Exception as e:
            print(f"FAISS build error: {e}")
            self.faiss_index = None

    # -----------------------------------------------------

    def numpy_search(self, query):

        if self.embeddings.shape[0] == 0:
            return None, 0

        sims = np.dot(self.embeddings, query)

        idx = int(np.argmax(sims))
        return idx, float(sims[idx])

    # -----------------------------------------------------

    def faiss_search(self, query):

        if not FAISS_AVAILABLE:
            return self.numpy_search(query)

        try:

            if self.faiss_index is None:

                if os.path.exists(self.faiss_index_file):
                    self.faiss_index = faiss.read_index(self.faiss_index_file)
                else:
                    self.build_faiss_index()

            if self.faiss_index is None:
                return self.numpy_search(query)

            query = np.array([self.normalize(query)], dtype="float32")

            scores, indices = self.faiss_index.search(query, 1)

            return int(indices[0][0]), float(scores[0][0])

        except Exception as e:
            print(f"FAISS search error: {e}")
            return self.numpy_search(query)

    # -----------------------------------------------------

    def search(self, instruction_text):

        if len(self.instructions) == 0:
            return None

        model = self.get_model()

        query = model.encode([instruction_text])[0].astype("float32")
        query = self.normalize(query)

        if len(self.instructions) < self.threshold:
            idx, score = self.numpy_search(query)
        else:
            idx, score = self.faiss_search(query)

        if idx is None or idx >= len(self.instructions):
            return None

        if score < self.similarity_threshold:
            return None

        print(f"Instruction memory match score: {score:.2f}")

        return self.instructions[idx]