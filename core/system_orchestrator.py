from core.system_mode_controller import SystemModeController
from core.dataset_pipeline_manager import DatasetPipelineManager
from core.runtime_dataset_trigger import RuntimeDatasetTrigger


class SystemOrchestrator:
    """
    Coordinates autonomous system behaviour.

    Handles:
    - mode switching
    - dataset pipeline trigger
    """

    def __init__(self):

        self.mode_controller = SystemModeController()

        self.dataset_trigger = RuntimeDatasetTrigger()

        self.pipeline_manager = DatasetPipelineManager()

    # -----------------------------------------------------

    def decide_mode(self, instruction=None):

        return self.mode_controller.decide_mode(instruction)

    # -----------------------------------------------------

    def handle_exploration_cycle(self):

        """
        Called after exploration cycle
        """

        trigger = self.dataset_trigger.should_trigger_pipeline()

        print(f"[DEBUG] Dataset trigger decision: {trigger}")

        if trigger:

            print("\nRunning automatic Phase2 pipeline")

            self.pipeline_manager.run_pipeline()

        else:
            print("[INFO] Dataset pipeline not triggered")

        # if self.dataset_trigger.should_trigger_pipeline():

        #     print("\nRunning automatic Phase2 pipeline")

        #     self.pipeline_manager.run_pipeline()

    # -----------------------------------------------------

    def handle_vln_cycle(self):

        """
        Placeholder for future VLN control logic
        """

        pass


# -----------------------------------------------------
# Test block
# -----------------------------------------------------

if __name__ == "__main__":

    orchestrator = SystemOrchestrator()

    mode = orchestrator.decide_mode()

    print("\nSystem mode:", mode)

    if mode == "explore":

        orchestrator.handle_exploration_cycle()

    else:

        orchestrator.handle_vln_cycle()