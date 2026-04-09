import os
import json
import time


class RuntimeDatasetTrigger:
    """
    Controls when Phase-2 dataset pipeline should run.

    Prevents continuous retraining.
    """

    def __init__(
        self,
        image_root="data/raw_images",
        state_file="data/runtime_state/pipeline_state.json",
        image_threshold=200
    ):

        self.image_root = image_root
        self.state_file = state_file
        self.image_threshold = image_threshold

        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)

        self.state = {
            "last_image_count": 0,
            "last_run_time": 0
        }

        self.load_state()

    # -----------------------------------------------------

    def load_state(self):

        if os.path.exists(self.state_file):

            try:

                with open(self.state_file, "r") as f:

                    self.state = json.load(f)

            except Exception:

                pass

    # -----------------------------------------------------

    def save_state(self):

        with open(self.state_file, "w") as f:

            json.dump(self.state, f, indent=4)

    # -----------------------------------------------------

    def count_images(self):

        total = 0

        for root, dirs, files in os.walk(self.image_root):

            for f in files:

                if f.lower().endswith(".png") or f.lower().endswith(".jpg"):

                    total += 1

        return total

    # -----------------------------------------------------

    def should_trigger_pipeline(self):

        """
        Decide whether dataset pipeline should run
        """

        current_count = self.count_images()

        last_count = self.state.get("last_image_count", 0)

        new_images = current_count - last_count

        if new_images >= self.image_threshold:

            print("\nDataset trigger activated")
            print("New images collected:", new_images)

            self.state["last_image_count"] = current_count
            self.state["last_run_time"] = time.time()

            self.save_state()

            return True

        return False


# -----------------------------------------------------
# Test block
# -----------------------------------------------------

if __name__ == "__main__":

    trigger = RuntimeDatasetTrigger()

    if trigger.should_trigger_pipeline():

        print("Pipeline should run")

    else:

        print("Pipeline not required yet")