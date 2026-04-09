import time


class ShutdownManager:

    """
    Handles safe shutdown of the system:
    - save data
    - compute metrics
    - land drone
    - release control
    """

    def __init__(
        self,
        client,
        visit_map,
        capture,
        map_metadata,
        metrics
    ):

        self.client = client
        self.visit_map = visit_map
        self.capture = capture
        self.map_metadata = map_metadata
        self.metrics = metrics

    # --------------------------------------------------

    def shutdown(self, start_time):

        """
        Perform safe shutdown sequence.
        """

        runtime = time.time() - start_time

        # ---------- SAVE DATA ----------

        try:
            self.visit_map.save()
        except Exception as e:
            print(f"Visit map save error: {e}")

        try:
            self.capture.save_metadata()
        except Exception as e:
            print(f"Capture metadata save error: {e}")

        try:
            self.map_metadata.save()
        except Exception as e:
            print(f"Map metadata save error: {e}")

        # ---------- METRICS ----------

        try:
            self.metrics.total_yaw_rotations = getattr(
                self.capture,
                "yaw_rotation_count",
                0
            )

            computed_metrics = self.metrics.compute(runtime)

        except Exception as e:
            print(f"Metrics computation error: {e}")
            computed_metrics = {}

        # ---------- LAND DRONE ----------

        try:
            self.client.landAsync().join()
        except Exception as e:
            print(f"Landing error: {e}")

        # ensure ground position (extra safety)
        try:
            self.client.moveToZAsync(0, 1).join()
        except Exception:
            pass

        # ---------- DISARM ----------

        try:
            self.client.armDisarm(False)
            self.client.enableApiControl(False)
        except Exception as e:
            print(f"Disarm error: {e}")

        # ---------- FINAL OUTPUT ----------

        # print("\nPHASE 1 COMPLETE")
        # print(computed_metrics)

        return computed_metrics