import subprocess
import sys
import os


class DatasetPipelineManager:
    """
    Automates Phase-2 dataset pipeline.

    Steps:
    1. Archive dataset
    2. Dataset integrity check
    3. Generate dataset index
    4. Run Phase-2 training
    """

    def __init__(self, project_root="."):

        self.project_root = project_root

    # -----------------------------------------------------

    def run_command(self, command):

        """
        Safely execute a python command
        """

        try:

            print("\nRunning:", command)

            subprocess.run(
                command,
                shell=True,
                check=True
            )

        except subprocess.CalledProcessError as e:

            print("Pipeline step failed:", e)

    # -----------------------------------------------------

    def archive_dataset(self):

        cmd = "python tools/archive_dataset_run.py"

        self.run_command(cmd)

    # -----------------------------------------------------

    def check_dataset(self):

        cmd = "python tools/check_dataset.py"

        self.run_command(cmd)

    # -----------------------------------------------------

    def generate_dataset_index(self):

        cmd = "python tools/generate_dataset_index.py"

        self.run_command(cmd)

    # -----------------------------------------------------

    def run_phase2_training(self):

        cmd = "python phase2/phase2_train.py"

        self.run_command(cmd)

    # -----------------------------------------------------

    def run_pipeline(self):

        """
        Execute full pipeline
        """

        print("\nStarting Dataset Pipeline")

        self.archive_dataset()

        self.check_dataset()

        self.generate_dataset_index()

        self.run_phase2_training()

        print("\nDataset Pipeline Completed")


# -----------------------------------------------------
# Test block
# -----------------------------------------------------

if __name__ == "__main__":

    manager = DatasetPipelineManager()

    manager.run_pipeline()