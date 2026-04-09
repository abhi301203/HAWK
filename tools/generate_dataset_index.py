import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.dataset_index_generator import DatasetIndexGenerator


def main():

    datasets_root = "datasets"

    for phase in os.listdir(datasets_root):

        phase_path = os.path.join(datasets_root, phase)

        if not os.path.isdir(phase_path):
            continue

        for domain_folder in os.listdir(phase_path):

            if not domain_folder.startswith("domain_"):
                continue

            domain_name = domain_folder.replace("domain_", "")

            dataset_path = os.path.join(phase_path, domain_folder)

            print("Generating index for:", dataset_path)

            gen = DatasetIndexGenerator(dataset_path, domain_name)

            gen.generate()


if __name__ == "__main__":
    main()