import os
import cv2
import time
import numpy as np

from HAWK.utils.airsim_utils import AirSimConnector
from HAWK.utils.logger import log_collision
from HAWK.utils.config import (
    IMAGE_PATH,
    COLLISION_LOG_PATH,
    FEATURE_PATH,
    FRAME_LIMIT,
    CAPTURE_DELAY
)

from HAWK.models.vision_encoder import VisionEncoder

print("SCRIPT STARTED")

# Ensure directories exist
os.makedirs(IMAGE_PATH, exist_ok=True)
os.makedirs(os.path.dirname(FEATURE_PATH), exist_ok=True)

connector = AirSimConnector()
encoder = VisionEncoder()

features_list = []

frame_id = 0

print("Starting Full Dataset Capture...")

while frame_id < FRAME_LIMIT:

    image = connector.get_image()

    if image is not None:

        # Save image
        filename = f"frame_{frame_id:04d}.png"
        cv2.imwrite(os.path.join(IMAGE_PATH, filename), image)
        print("Saved image:", filename)

        # Extract features
        features = encoder.extract_features(image)
        features_list.append(features)

    position = connector.get_position()

    if connector.get_collision():
        log_collision(COLLISION_LOG_PATH, position)
        print("Collision logged at:", position)

    frame_id += 1
    time.sleep(CAPTURE_DELAY)

# Save features to disk
features_array = np.array(features_list)
np.save(FEATURE_PATH, features_array)

print("Feature dataset saved.")
print("Data Capture Complete.")