"""
Simple navigation decision model (placeholder for learning model)
"""

import numpy as np


class NavigationModel:
    def __init__(self):
        print("Navigation Model Initialized")

    def decide_action(self, features):
        """
        Dummy logic for now
        """
        # Example simple heuristic
        if np.mean(features) > 0.5:
            return "MOVE_FORWARD"
        else:
            return "TURN_RIGHT"