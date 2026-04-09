import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tools.dataset_integrity_checker import DatasetIntegrityChecker

if __name__ == "__main__":

    dataset_root = "datasets/phase1_v1"

    for domain in os.listdir(dataset_root):

        domain_path = os.path.join(dataset_root, domain)

        if not os.path.isdir(domain_path):
            continue

        print("\nChecking dataset:", domain)

    checker = DatasetIntegrityChecker(domain_path)

    checker.run()