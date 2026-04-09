import time


class WarmupExplorer:

    """
    Performs short exploration before VLN execution.

    Purpose:
    - give spatial awareness
    - populate map metadata
    - initialize spatial graph
    """

    def __init__(
        self,
        movement,
        visit_map,
        map_metadata,
        vln_controller,
        step_size,
        altitude,
        speed,
        warmup_time
    ):

        self.movement = movement
        self.visit_map = visit_map
        self.map_metadata = map_metadata
        self.vln_controller = vln_controller

        self.step_size = step_size
        self.altitude = altitude
        self.speed = speed
        self.warmup_time = warmup_time

    # --------------------------------------------------

    def run(self):

        print("\nStarting perception-based warmup...")

        start_time = time.time()

        while time.time() - start_time < self.warmup_time:

            current_pos = self.movement.get_position()

            # --------------------------------------------------
            # STEP 1: 360° ROTATION (NO RANDOM MOVEMENT)
            # --------------------------------------------------

            for yaw in [0, 90, 180, 270]:

                try:
                    self.movement.client.rotateToYawAsync(yaw).join()
                    self.movement.client.hoverAsync().join()
                    time.sleep(0.3)
                except:
                    pass

                # --------------------------------------------------
                # STEP 2: CAPTURE IMAGE
                # --------------------------------------------------

                frame = None

                try:
                    frame = self.movement.capture_image()
                except Exception:
                    pass

                if frame is None:
                    continue

                # --------------------------------------------------
                # STEP 3: PERCEPTION (LIGHTWEIGHT)
                # --------------------------------------------------

                try:
                    detections = self.vln_controller.landmark_detector.detect(
                        frame,
                        drone_position=current_pos,
                        drone_yaw=yaw
                    )

                    if detections:
                        print("Warmup detections:", [d.get("label") for d in detections])

                except Exception:
                    pass

            # --------------------------------------------------
            # STEP 4: SMALL RANDOM SHIFT (OPTIONAL)
            # --------------------------------------------------

            cx, cy = current_pos

            import random

            dx = random.uniform(-2, 2)
            dy = random.uniform(-2, 2)

            try:
                self.movement.move_to(
                    cx + dx,
                    cy + dy,
                    self.altitude,
                    self.speed
                )
            except:
                pass

        print("Warmup perception finished")