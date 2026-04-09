"""
Run autonomous navigation
"""

from HAWK.utils.airsim_utils import AirSimConnector
from HAWK.models.vision_encoder import VisionEncoder
from HAWK.models.navigation_model import NavigationModel

connector = AirSimConnector()
encoder = VisionEncoder()
navigator = NavigationModel()

print("Starting Navigation Loop...")

image = connector.get_image()

if image is not None:
    features = encoder.extract_features(image)
    action = navigator.decide_action(features)

    print("Decided Action:", action)