import numpy as np
import json
import os


class EmbeddingDatabase:

    def __init__(self, domain):

        self.base_path = f"data/features/{domain}"

        os.makedirs(self.base_path, exist_ok=True)

    def save_embeddings(self, embeddings, image_paths):

        embeddings = np.array(embeddings)

        np.save(f"{self.base_path}/embeddings.npy", embeddings)

        with open(f"{self.base_path}/image_paths.json", "w") as f:
            json.dump(image_paths, f, indent=4)

    def save_signature(self, signature):

        if signature is None:
            return

        np.save(f"{self.base_path}/domain_signature.npy", signature)