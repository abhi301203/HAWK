import airsim
import numpy as np


class AirSimConnector:
    def __init__(self):
        # Connect to AirSim
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()

        # Enable control
        self.client.enableApiControl(True)
        self.client.armDisarm(True)

        print("Connected to AirSim")

    def get_image(self):
        """
        Capture RGB image from drone front camera
        """
        responses = self.client.simGetImages([
            airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
        ])

        response = responses[0]

        if response.width == 0:
            return None

        img1d = np.frombuffer(response.image_data_uint8, dtype=np.uint8)
        img_rgb = img1d.reshape(response.height, response.width, 3)

        return img_rgb

    def get_position(self):
        """
        Get current drone position (x, y, z)
        """
        state = self.client.getMultirotorState()
        pos = state.kinematics_estimated.position

        return (pos.x_val, pos.y_val, pos.z_val)

    def get_collision(self):
        """
        Check if drone has collided
        """
        collision = self.client.simGetCollisionInfo()
        return collision.has_collided

    def takeoff(self):
        """
        Takeoff command
        """
        self.client.takeoffAsync().join()

    def land(self):
        """
        Land command
        """
        self.client.landAsync().join()

    def move_by_velocity(self, vx, vy, vz, duration):
        """
        Move drone using velocity control
        """
        self.client.moveByVelocityAsync(vx, vy, vz, duration).join()