import numpy as np
import airsim

def get_position(client):
    pos = client.getMultirotorState().kinematics_estimated.position
    return np.array([pos.x_val, pos.y_val])

def move_step(client, vx, vy, duration=2):
    start = get_position(client)
    client.moveByVelocityAsync(vx, vy, 0, duration).join()
    end = get_position(client)
    return np.linalg.norm(end - start)