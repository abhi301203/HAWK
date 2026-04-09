import os


class DatasetDiscovery:

    def __init__(self, datasets_root="datasets"):

        self.datasets_root = datasets_root

    def discover(self):

        datasets = []

        for phase in os.listdir(self.datasets_root):

            phase_path = os.path.join(self.datasets_root, phase)

            if not os.path.isdir(phase_path):
                continue

            for domain_folder in os.listdir(phase_path):

                if not domain_folder.startswith("domain_"):
                    continue

                domain_name = domain_folder.replace("domain_", "")

                datasets.append({

                    "domain": domain_name,
                    "path": os.path.join(phase_path, domain_folder)

                })

        return datasets