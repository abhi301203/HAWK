import os
import numpy as np
import cv2

from phase2.feature_extractor import FeatureExtractor
from phase2.adaptive_memory import AdaptiveMemory


class DomainDetector:

    def __init__(self, client, signatures_path="data/features"):

        self.client = client

        self.extractor = FeatureExtractor()

        self.signatures = {}

        self.runtime_memory = AdaptiveMemory("runtime")

        if os.path.exists(signatures_path):

            for domain in os.listdir(signatures_path):

                sig_path = os.path.join(
                    signatures_path,
                    domain,
                    "domain_signature.npy"
                )

                if os.path.exists(sig_path):

                    self.signatures[domain] = np.load(sig_path)

    # -----------------------------

    def cosine_similarity(self, a, b):

        dot = np.dot(a, b)

        norm = np.linalg.norm(a) * np.linalg.norm(b)

        if norm == 0:
            return 0

        return dot / norm

    # -----------------------------

    def detect_map_from_airsim(self):

        try:

            settings = self.client.getSettingsString().lower()

            if "blocks" in settings:
                return "blocks"

            if "city" in settings:
                return "city"

            if "coastline" in settings:
                return "coastline"

            if "neighborhood" in settings:
                return "neighborhood"

            return None

        except:
            return None

    # -----------------------------

    def detect(self, client, capture_frame_func):

        base_map = self.detect_map_from_airsim()

        embeddings = []

        # capture multiple frames (few-shot detection)
        for _ in range(3):

            # frame = capture_frame_func(client)
            try:
                frame = capture_frame_func(client)
            except:
                frame = capture_frame_func()

            if frame is None:
                continue

            # temp_path = "temp_domain_frame.jpg"

            frame = frame.astype(np.uint8)

            # cv2.imwrite(temp_path, frame)
            # emb = self.extractor.extract(temp_path)
            try:
                emb = self.extractor.extract_from_array(frame)
            except:
                # fallback to old method (safety)
                temp_path = "temp_domain_frame.jpg"
                cv2.imwrite(temp_path, frame)
                emb = self.extractor.extract(temp_path)

            embeddings.append(emb)

            # Adaptive Cross Domain Memory  runtime learning
            # self.runtime_memory.add_embedding(emb)

        if len(embeddings) == 0:

            if base_map:
                return base_map + "_unknown"

            return "unknown_domain"

        emb = np.mean(embeddings, axis=0)

        # ------------adaptive runtime memory update------------
        runtime_key = base_map if base_map else "unknown"

        # if not self.runtime_memory.exists(runtime_key):
        #     self.runtime_memory[runtime_key] = AdaptiveMemory(runtime_key)
        # if runtime_key not in self.runtime_memory:
        #     self.runtime_memory[runtime_key] = AdaptiveMemory(runtime_key)

        # store embedding in runtime memory for future signature updates
        self.runtime_memory.add_embedding(emb)
        # self.runtime_memory[runtime_key].add_embedding(emb)

        best_domain = None
        best_score = -1

        for domain, signature in self.signatures.items():

            score = self.cosine_similarity(emb, signature)

            if score > best_score:

                best_score = score
                best_domain = domain

        if best_domain and best_score > 0.75:
            return best_domain

        if base_map:
            return base_map + "_unknown"

        return "unknown_domain"