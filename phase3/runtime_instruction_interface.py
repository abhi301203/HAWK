class RuntimeInstructionInterface:

    """
    Handles runtime instruction input.

    Supported modes:
    - exploration (ENTER)
    - navigation instruction
    - debug commands
    - clarification dialog
    """

    def __init__(self):

        self.debug_commands = {
            "help",
            "exit",
            "status",
            "memory"
        }

        # stores latest instruction for clarification dialogue
        self.last_instruction = None

    # --------------------------------------------------

    def show_prompt(self):

        print("\n---------------------------------")
        print("Enter navigation instruction")
        print("(Press ENTER for exploration mode)")
        print("Commands: help | status | memory | exit")
        print("---------------------------------")

    # --------------------------------------------------

    def classify_input(self, text):

        """
        Determine input type
        """

        if text == "":
            return "explore"

        if text.lower() in self.debug_commands:
            return "command"

        return "instruction"

    # --------------------------------------------------

    def get_instruction(self):

        """
        Ask user for instruction.
        """

        try:

            self.show_prompt()

            text = input("Instruction: ")

            if text is None:
                return None

            text = text.strip()

            mode = self.classify_input(text)

            # ---------------------------
            # Exploration mode
            # ---------------------------

            if mode == "explore":

                return {
                    "type": "explore",
                    "value": None
                }

            # ---------------------------
            # Debug command
            # ---------------------------

            if mode == "command":

                return {
                    "type": "command",
                    "value": text.lower()
                }

            # ---------------------------
            # Navigation instruction
            # ---------------------------

            self.last_instruction = text

            return {
                "type": "instruction",
                "value": text
            }

        except KeyboardInterrupt:

            print("\nInstruction input cancelled")

            return None

    # --------------------------------------------------

    def ask_clarification(self, question):

        """
        Used when drone needs clarification.

        Example:
        Drone: I see multiple cars. Which one?
        """

        try:

            print("\nDrone clarification:")
            print(question)

            response = input("User guidance: ")

            if response is None:
                return None

            response = response.strip()

            if response == "":
                return None

            return response

        except KeyboardInterrupt:

            print("\nClarification cancelled")

            return None