import numpy as np
import time


class DroneMovement:

    def __init__(self, client, collision_memory=None, metrics=None):

        self.client = client
        self.collision_memory = collision_memory
        self.metrics = metrics

    # ---------------------------------------

    def get_position(self):

        pos = self.client.getMultirotorState().kinematics_estimated.position

        return np.array([float(pos.x_val), float(pos.y_val)])

    # ---------------------------------------

    def move_to(self, x, y, z, speed):

        try:

            start_pos = self.get_position()

            target = np.array([x, y])

            distance_goal = np.linalg.norm(target - start_pos)

            # dynamic timeout based on distance
            timeout = max(12, distance_goal / speed * 3)

            future = self.client.moveToPositionAsync(x, y, z, speed)

            start_time = time.time()

            last_progress_time = start_time
            last_position = start_pos

            while True:

                time.sleep(0.2)

                current_pos = self.get_position()

                collision = self.client.simGetCollisionInfo()

                # -------- COLLISION DETECTED --------
                if collision.has_collided:

                    pos = self.client.getMultirotorState().kinematics_estimated.position

                    if self.collision_memory is not None:
                        try:
                            self.collision_memory.register_collision(
                                pos.x_val,
                                pos.y_val
                            )
                        except:
                            pass

                    if self.metrics is not None:
                        self.metrics.collisions += 1

                    future.cancel()

                    return False, 0

                # -------- CHECK SUCCESS --------
                distance_to_target = np.linalg.norm(current_pos - target)

                if distance_to_target < 1.0:

                    travelled = np.linalg.norm(current_pos - start_pos)

                    return True, float(travelled)

                # -------- CHECK PROGRESS --------
                progress = np.linalg.norm(current_pos - last_position)

                if progress > 0.25:
                    last_progress_time = time.time()
                    last_position = current_pos

                # -------- STUCK DETECTION --------
                if time.time() - last_progress_time > 3:

                    if self.metrics is not None:
                        self.metrics.stuck_events += 1

                    pos = self.client.getMultirotorState().kinematics_estimated.position

                    try:

                        # -------- SMART ESCAPE VECTOR --------

                        # bias escape opposite to goal
                        escape_x = pos.x_val - x
                        escape_y = pos.y_val - y

                        escape_x += np.random.uniform(-0.5, 0.5)
                        escape_y += np.random.uniform(-0.5, 0.5)

                        # apply collision memory repulsion
                        if self.collision_memory is not None:

                            px = pos.x_val
                            py = pos.y_val

                            try:
                                memory_points = list(self.collision_memory.data)
                            except:
                                memory_points = []

                            for ox, oy in memory_points:

                                dx = px - ox
                                dy = py - oy

                                dist = np.sqrt(dx*dx + dy*dy)

                                if dist < 8 and dist > 0.1:

                                    repulse = (8 - dist) / 8

                                    escape_x += (dx / dist) * repulse * 3
                                    escape_y += (dy / dist) * repulse * 3

                        # normalize vector
                        norm = np.sqrt(escape_x**2 + escape_y**2)

                        if norm > 0:
                            escape_x /= norm
                            escape_y /= norm

                        # perform escape move
                        self.client.moveByVelocityAsync(
                            escape_x * 2,
                            escape_y * 2,
                            0,
                            1.5
                        ).join()

                        if self.metrics is not None:
                            self.metrics.successful_escapes += 1

                    except:
                        pass

                    future.cancel()

                    return False, 0

                # -------- GLOBAL TIMEOUT --------
                if time.time() - start_time > timeout:

                    if self.metrics is not None:
                        self.metrics.stuck_events += 1

                    future.cancel()

                    return False, 0

        except:
            return False, 0

    # ---------------------------------------

    def move_to_altitude(self, z):

        self.client.moveToZAsync(z, 1).join()