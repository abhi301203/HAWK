import json
import os


class SystemModeController:
    """
    Controls system operation mode.

    Modes:
    - explore : phase1 exploration + dataset generation
    - vln     : instruction-based navigation

    Priority logic:
    1. If instruction exists → VLN mode
    2. If config forces explore → explore mode
    3. Otherwise → explore mode
    """

    def __init__(self, config_path="config.json"):

        self.config_path = config_path
        self.mode = "explore"

        self.load_config()

    # -----------------------------------------------------

    def load_config(self):

        """
        Load mode from config file if present
        """

        if not os.path.exists(self.config_path):

            return

        try:

            with open(self.config_path, "r") as f:

                config = json.load(f)

                if "mode" in config:

                    self.mode = config["mode"]

        except Exception:

            self.mode = "explore"

    # -----------------------------------------------------

    def decide_mode(self, instruction=None):

        """
        Decide system mode based on instruction presence
        """

        if instruction is not None and instruction.strip() != "":

            return "vln"

        return self.mode

    # -----------------------------------------------------

    def is_explore_mode(self, instruction=None):

        return self.decide_mode(instruction) == "explore"

    # -----------------------------------------------------

    def is_vln_mode(self, instruction=None):

        return self.decide_mode(instruction) == "vln"


# -----------------------------------------------------
# Test block
# -----------------------------------------------------

if __name__ == "__main__":

    controller = SystemModeController()

    print("\nMode without instruction:")
    print(controller.decide_mode())

    print("\nMode with instruction:")
    print(controller.decide_mode("go to the building"))