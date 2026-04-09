import numpy as np
import random


class DomainSignature:

    def compute(self, embeddings, sample_size=500):

        """
        Compute stable domain signature using balanced sampling.
        """

        if len(embeddings) == 0:
            return None

        embeddings = np.array(embeddings)

        # shuffle embeddings to avoid bias
        indices = list(range(len(embeddings)))
        random.shuffle(indices)

        # select balanced subset
        if len(indices) > sample_size:
            indices = indices[:sample_size]

        sampled = embeddings[indices]

        signature = np.mean(sampled, axis=0)

        return signature


    def similarity(self, sig1, sig2):

        """
        Cosine similarity between two domain signatures
        """

        if sig1 is None or sig2 is None:
            return 0

        dot = np.dot(sig1, sig2)

        norm = np.linalg.norm(sig1) * np.linalg.norm(sig2)

        if norm == 0:
            return 0

        return dot / norm