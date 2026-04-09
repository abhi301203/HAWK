import os
import numpy as np


class AdaptiveMemory:

    def __init__(self, domain,
                 memory_root="data/runtime_memory",
                 threshold=25):

        """
        Adaptive Cross-Domain Memory (ACDM)

        domain      : current environment domain
        threshold   : number of embeddings required
                      before updating runtime signature
        """

        self.domain = domain
        self.threshold = threshold

        self.memory_path = os.path.join(memory_root, domain)

        os.makedirs(self.memory_path, exist_ok=True)

        # runtime buffer
        self.buffer = []

    # -------------------------------------------------

    def add_embedding(self, embedding):

        """
        Add new embedding to runtime buffer
        """

        self.buffer.append(embedding)

        # Few-shot trigger
        if len(self.buffer) >= self.threshold:

            self.update_runtime_signature()

            # clear buffer after update
            self.buffer = []

    # -------------------------------------------------

    def buffer_size(self):

        return len(self.buffer)

    # -------------------------------------------------

    def compute_signature(self):

        """
        Compute mean embedding signature
        """

        if len(self.buffer) == 0:
            return None

        embeddings = np.array(self.buffer)

        signature = np.mean(embeddings, axis=0)

        return signature

    # -------------------------------------------------

    def update_runtime_signature(self):

        """
        Save runtime domain signature
        """

        signature = self.compute_signature()

        if signature is None:
            return

        path = os.path.join(
            self.memory_path,
            "runtime_signature.npy"
        )

        np.save(path, signature)

        print("ACDM runtime signature updated:", self.domain)

    # -------------------------------------------------

    def save_runtime_embeddings(self):

        """
        Save collected embeddings for analysis
        """

        if len(self.buffer) == 0:
            return

        embeddings = np.array(self.buffer)

        path = os.path.join(
            self.memory_path,
            "runtime_embeddings.npy"
        )

        np.save(path, embeddings)

    # -------------------------------------------------

    def load_runtime_signature(self):

        """
        Load previously saved runtime signature
        """

        path = os.path.join(
            self.memory_path,
            "runtime_signature.npy"
        )

        if os.path.exists(path):

            return np.load(path)

        return None

    # -------------------------------------------------

    def clear_buffer(self):

        self.buffer = []