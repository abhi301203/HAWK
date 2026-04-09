import airsim
import numpy as np
import os
import json
import time
from datetime import datetime


class ImageCaptureManager:

    def __init__(self, client, run_folder):

        self.client = client
        self.run_folder = run_folder

        # Metadata file path
        self.metadata_file = os.path.join(run_folder, "metadata.json")

        # Metadata storage
        self.metadata_records = []

        # Image counter
        self.image_count = 0

        # Ensure run folder exists
        os.makedirs(self.run_folder, exist_ok=True)

        self.yaw_rotation_count = 0


    # --------------------------------------------------

    def capture(self, capture_four):

        previous_yaw = None

        # store captured image ids for metadata linking
        captured_ids = []

        if not capture_four:

            # face forward
            self.client.rotateToYawAsync(0).join()
            self.client.hoverAsync().join()

            time.sleep(0.4)

            self.yaw_rotation_count += 1

            # capture image
            image_id = self.capture_image(0)

            if image_id is not None:
                captured_ids.append(image_id)

            # save ids for metadata manager
            self.last_capture_ids = captured_ids
            return

        # Capture four directions
        for yaw in [0, 90, 180, 270]:

            if previous_yaw is None or yaw != previous_yaw:

                # rotate drone
                self.client.rotateToYawAsync(yaw).join()

                # stabilize camera
                self.client.hoverAsync().join()

                # stabilization delay
                time.sleep(0.4)

                # count rotation
                self.yaw_rotation_count += 1

                # capture image
                image_id = self.capture_image(yaw)

                if image_id is not None:
                    captured_ids.append(image_id)

                previous_yaw = yaw

        # IMPORTANT: save captured ids so hawk_train can read them
        self.last_capture_ids = captured_ids

    # --------------------------------------------------

    def capture_image(self, yaw_angle):

        responses = self.client.simGetImages([
            airsim.ImageRequest(
                "0",
                airsim.ImageType.Scene,
                False,
                False
            )
        ])

        if not responses:
            return None

        response = responses[0]

        if response.width == 0:
            return None

        img = np.frombuffer(
            response.image_data_uint8,
            dtype=np.uint8
        )

        img = img.reshape(
            response.height,
            response.width,
            3
        )

        # unique image name
        image_name = f"img_{int(time.time()*1000)}_{self.image_count}.png"

        image_path = os.path.join(
            self.run_folder,
            image_name
        )

        # small stabilization delay
        time.sleep(0.2)

        airsim.write_png(image_path, img)

        # Get drone state for metadata
        state = self.client.getMultirotorState()

        pos = state.kinematics_estimated.position
        orientation = state.kinematics_estimated.orientation

        yaw_actual = airsim.to_eularian_angles(orientation)[2]

        metadata_entry = {

            "image_name": image_name,

            "x": float(pos.x_val),
            "y": float(pos.y_val),
            "z": float(pos.z_val),

            "yaw_command": float(yaw_angle),
            "yaw_actual": float(yaw_actual),

            "timestamp": datetime.now().isoformat()
        }

        self.metadata_records.append(metadata_entry)

        self.image_count += 1

        # IMPORTANT: return image name for map metadata linking
        return image_name

    # --------------------------------------------------

    def save_metadata(self):

        with open(self.metadata_file, "w") as f:
            json.dump(
                self.metadata_records,
                f,
                indent=4
            )