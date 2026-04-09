import airsim
import numpy as np
import cv2


def capture_frame(client):

    responses = client.simGetImages([
        airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
    ])

    if not responses:
        return None

    response = responses[0]

    img = np.frombuffer(response.image_data_uint8, dtype=np.uint8)

    img = img.reshape(response.height, response.width, 3)

    return img