import numpy as np
import random


class EscapeSystem:

    def __init__(self, client):

        self.client = client

    # ---------------------------------------

    def escape(self):

        try:

            state = self.client.getMultirotorState()

            pos = state.kinematics_estimated.position

            # STEP 1: move upward to clear obstacle
            self.client.moveToZAsync(pos.z_val - 2, 1).join()

            # STEP 2: random horizontal escape direction
            directions = [
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1)
            ]

            dx, dy = random.choice(directions)

            self.client.moveByVelocityAsync(
                dx,
                dy,
                0,
                1.5
            ).join()

            # STEP 3: stabilize
            self.client.hoverAsync().join()

            # STEP 4: verify collision cleared
            collision = self.client.simGetCollisionInfo()

            if collision.has_collided:

                try:
                    pos = self.client.getMultirotorState().kinematics_estimated.position

                    # small escape maneuver
                    self.client.moveByVelocityAsync(-1,0,0,1).join()
                    self.client.moveToZAsysnc(pos.z_val - 1.5, 1).join()

                except:
                    pass

                return False, 0

            return True

        except:

            return False