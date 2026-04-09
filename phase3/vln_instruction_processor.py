import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from phase3.runtime_instruction_interface import RuntimeInstructionInterface
from phase3.instruction_parser import InstructionParser
from phase3.instruction_memory import InstructionMemory


class VLNInstructionProcessor:
    """
    Processes runtime navigation instructions.

    Handles:
    - instruction input
    - instruction parsing
    - task normalization
    - instruction memory storage
    """

    def __init__(self):

        self.interface = RuntimeInstructionInterface()

        self.parser = InstructionParser()

        self.memory = InstructionMemory()

    # --------------------------------------------------

    def normalize_task(self, parsed):

        """
        Convert parsed tokens into structured task
        """

        task = {
            "type": "generic_navigation",
            "target_object": None,
            "target_color": None,
            "primary_action": None,
            "modifier": None,
            "secondary_action": None,
            "count": None,
            "directions": parsed.get("directions", [])
        }

        actions = parsed.get("actions", [])
        landmarks = parsed.get("landmarks", [])
        colors = parsed.get("colors", [])
        modifiers = parsed.get("modifiers", [])
        counts = parsed.get("counts", [])

        if len(actions) > 0:
            task["primary_action"] = actions[0]

        if len(actions) > 1:
            task["secondary_action"] = actions[1]

        if len(landmarks) > 0:
            task["target_object"] = landmarks[0]
            task["type"] = "object_navigation"

        if len(colors) > 0:
            task["target_color"] = colors[0]

        if len(modifiers) > 0:
            task["modifier"] = modifiers[0]

        if len(counts) > 0:
            try:
                task["count"] = int(counts[0])
            except:
                task["count"] = counts[0]

        return task

    # --------------------------------------------------

    def get_and_process_instruction(self):

        """
        Receive instruction and convert into structured command
        """

        instruction = self.interface.get_instruction()

        if instruction is None:

            return None

        parsed = self.parser.parse(instruction)

        task = self.normalize_task(parsed)

        # store instruction in episodic memory
        try:
            self.memory.store_instruction(instruction, task)
        except Exception:
            pass

        return task


# --------------------------------------------------
# Test block
# --------------------------------------------------

if __name__ == "__main__":

    processor = VLNInstructionProcessor()

    result = processor.get_and_process_instruction()

    if result:

        print("\nStructured Task:\n")
        print(result)

    else:

        print("\nExploration mode triggered")