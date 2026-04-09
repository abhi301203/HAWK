import sys
import os
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from multiprocessing import Pool
from tools.dataset_discovery import DatasetDiscovery
from tools.dataset_loader import HawkDatasetLoader
from phase2.feature_extractor import FeatureExtractor
from phase2.domain_signature import DomainSignature
from phase2.embedding_database import EmbeddingDatabase


def extract_worker(args):

    extractor, image_path = args

    return extractor.extract(image_path)


def run_phase2():

    finder = DatasetDiscovery()

    datasets = finder.discover()

    extractor = FeatureExtractor()

    for ds in datasets:

        loader = HawkDatasetLoader(ds["path"])

        data = loader.load_images_with_metadata()

        image_paths = [item["image"] for item in data]

        with Pool(4) as p:
            embeddings = p.map(extract_worker, [(extractor, path) for path in image_paths])

        domain = ds["domain"]

        db = EmbeddingDatabase(domain)

        db.save_embeddings(embeddings, image_paths)

        sig = DomainSignature().compute(embeddings)

        db.save_signature(sig)

        print(f"Processed domain: {domain}")


if __name__ == "__main__":
    run_phase2()