import airsim
import numpy as np
import os
import time
import json
import math


class HawkTrainerV4:

    def __init__(self):

        print("Initializing HawkTrainer V4...")

        # ---------------- CONFIG ----------------
        self.GRID_SIZE = 20              # total half-span meters
        self.STEP_SIZE = 2
        self.ALTITUDES = [-5, -7]
        self.MAX_IMAGES = 2000
        self.MAX_RUNTIME = 15 * 60
        self.COLLISION_RADIUS = 2.0
        self.ESCAPE_COOLDOWN = 3
        self.STUCK_THRESHOLD = 0.5

        # ---------------- METRICS ----------------
        self.images_captured = 0
        self.collisions = 0
        self.successful_escapes = 0
        self.distance_travelled = 0
        self.last_escape_time = 0

        # ---------------- PATHS ----------------
        self.base_path = os.getcwd()
        self.image_path = os.path.join(self.base_path, "data", "raw_images")
        self.collision_file = os.path.join(self.base_path, "data", "collision_logs", "collision_memory.json")
        self.metrics_file = os.path.join(self.base_path, "data", "collision_logs", "run_metrics.json")

        os.makedirs(self.image_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.collision_file), exist_ok=True)

        # ---------------- LOAD MEMORY ----------------
        self.locked_zones = self.load_collision_memory()

        # Continue image numbering safely
        self.images_captured = len(os.listdir(self.image_path))

        # ---------------- CONNECT ----------------
        print("Connecting to AirSim...")
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)
        print("Connected to AirSim.")

    # --------------------------------------------------------

    def load_collision_memory(self):
        if os.path.exists(self.collision_file):
            with open(self.collision_file, "r") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    # --------------------------------------------------------

    def save_collision_memory(self):
        with open(self.collision_file, "w") as f:
            json.dump(self.locked_zones, f, indent=4)

    # --------------------------------------------------------

    def save_metrics(self, runtime):
        metrics = {
            "collisions": self.collisions,
            "successful_escapes": self.successful_escapes,
            "images_captured": self.images_captured,
            "distance_travelled": round(self.distance_travelled, 2),
            "runtime_minutes": round(runtime / 60, 2),
            "locked_collision_zones": len(self.locked_zones)
        }

        with open(self.metrics_file, "w") as f:
            json.dump(metrics, f, indent=4)

        print("\nTraining Complete")
        print(json.dumps(metrics, indent=4))

    # --------------------------------------------------------

    def takeoff(self):
        self.client.takeoffAsync().join()
        time.sleep(1)

    def move_to_altitude(self, z):
        self.client.moveToZAsync(z, 1).join()

    def land(self):
        self.client.landAsync().join()
        self.client.armDisarm(False)
        self.client.enableApiControl(False)

    # --------------------------------------------------------

    def get_position(self):
        pos = self.client.getMultirotorState().kinematics_estimated.position
        return np.array([pos.x_val, pos.y_val])

    # --------------------------------------------------------

    def capture_images(self):
        responses = self.client.simGetImages([
            airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)
        ])

        if responses and responses[0].width > 0:
            img = np.frombuffer(responses[0].image_data_uint8, dtype=np.uint8)
            img = img.reshape(responses[0].height, responses[0].width, 3)

            filename = os.path.join(
                self.image_path,
                f"img_{self.images_captured}.png"
            )
            airsim.write_png(filename, img)
            self.images_captured += 1

    # --------------------------------------------------------

    def is_collision(self):
        return self.client.simGetCollisionInfo().has_collided

    # --------------------------------------------------------

    def is_locked_zone(self, position):
        for zone in self.locked_zones:
            if np.linalg.norm(position - np.array(zone)) < self.COLLISION_RADIUS:
                return True
        return False

    # --------------------------------------------------------

    def escape(self):
        if time.time() - self.last_escape_time < self.ESCAPE_COOLDOWN:
            return

        self.last_escape_time = time.time()
        print("Escape triggered...")

        # Immediate stop
        self.client.moveByVelocityAsync(0, 0, 0, 0.5).join()

        # Backward shift
        self.client.moveByVelocityAsync(-1, 0, 0, 1).join()

        # Lateral shift
        self.client.moveByVelocityAsync(0, 1, 0, 1).join()

        self.successful_escapes += 1

    # --------------------------------------------------------

    def move_step(self, vx, vy):
        start = self.get_position()

        self.client.moveByVelocityAsync(vx, vy, 0, 1).join()

        end = self.get_position()
        displacement = np.linalg.norm(end - start)

        if displacement > self.STUCK_THRESHOLD:
            self.distance_travelled += displacement
            return True
        else:
            return False

    # --------------------------------------------------------

    def run(self):

        self.takeoff()
        start_time = time.time()

        half_steps = int(self.GRID_SIZE / self.STEP_SIZE)

        for altitude in self.ALTITUDES:

            self.move_to_altitude(altitude)

            direction = 1

            for row in range(-half_steps, half_steps):

                for col in range(-half_steps, half_steps):

                    if time.time() - start_time > self.MAX_RUNTIME:
                        print("Runtime limit reached.")
                        self.land()
                        self.save_collision_memory()
                        self.save_metrics(time.time() - start_time)
                        return

                    if self.images_captured >= self.MAX_IMAGES:
                        print("Image limit reached.")
                        self.land()
                        self.save_collision_memory()
                        self.save_metrics(time.time() - start_time)
                        return

                    moved = self.move_step(direction * self.STEP_SIZE, 0)

                    if not moved:
                        if self.is_collision():
                            self.collisions += 1
                            pos = self.get_position().tolist()

                            if not self.is_locked_zone(np.array(pos)):
                                self.locked_zones.append(pos)

                            self.escape()
                        else:
                            self.escape()
                    else:
                        self.capture_images()

                # shift to next row (Y direction)
                moved = self.move_step(0, self.STEP_SIZE)
                if not moved:
                    self.escape()

                direction *= -1

        self.land()
        self.save_collision_memory()
        self.save_metrics(time.time() - start_time)


# ------------------------------------------------------------

if __name__ == "__main__":
    print("STARTING HAWK V4 FINAL...")
    trainer = HawkTrainerV4()
    trainer.run()