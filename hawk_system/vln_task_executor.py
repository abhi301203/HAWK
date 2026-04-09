import math
import time


class VLNTaskExecutor:

    def __init__(
        self,
        movement,
        landmark_memory,
        landmark_detector,
        vln_controller,
        search_function,
        altitude,
        speed
    ):

        self.movement = movement
        self.landmark_memory = landmark_memory
        self.landmark_detector = landmark_detector
        self.vln_controller = vln_controller

        self.search_for_target_object = search_function

        self.altitude = altitude
        self.speed = speed

    # --------------------------------------------------

    def execute(self, instruction, map_metadata):

        detection_success = False # track real detection success  

        print("\nProcessing VLN instruction...")

        # ---------- STEP 0: PARSE ----------
        try:
            instruction_data = self.vln_controller.process_instruction(instruction)
        except Exception as e:
            print(f"Instruction parsing failed: {e}")
            return

        subtasks = instruction_data.get("subtasks", [])

        if not subtasks:
            print("Invalid instruction")
            return

        target_found = False

        # --------------------------------------------------
        # STEP 1: PROCESS TASKS
        # --------------------------------------------------

        for task in subtasks:

            landmarks = task.get("landmarks", [])

            if not landmarks:
                continue

            target = landmarks[0]

            print(f"\nSearching for landmark: {target}")

            current_pos = self.movement.get_position()

            # --------------------------------------------------
            # STEP 2: MEMORY RANKING (SAFE VERSION)
            # --------------------------------------------------

            best_entry = None
            best_score = 0

            try:
                candidates = self.landmark_memory.get_landmarks(target)
            except:
                candidates = []

            for entry in candidates:

                score = self._score_memory(entry, current_pos)

                if score > best_score:
                    best_score = score
                    best_entry = entry

            # --------------------------------------------------
            # SAFE MEMORY USAGE (FIXED)
            # --------------------------------------------------

            use_memory = False

            if best_entry:

                target_pos = best_entry.get("pos")

                if target_pos:

                    dx = target_pos[0] - current_pos[0]
                    dy = target_pos[1] - current_pos[1]
                    distance = (dx**2 + dy**2) ** 0.5

                    print(f"Memory score: {best_score:.4f} | distance: {distance:.2f}m")

                    # ---------- VERY CLOSE → DIRECT MOVE ----------
                    if best_score > 0.15 and distance < 15:

                        print("Strong memory → moving directly")
                        use_memory = True

                    # ---------- MEDIUM DISTANCE → GUIDE SEARCH ----------
                    elif best_score > 0.1 and distance < 30:

                        print("Memory used as guidance → moving halfway")

                        mid_x = current_pos[0] + 0.5 * dx
                        mid_y = current_pos[1] + 0.5 * dy

                        if self._move_to((mid_x, mid_y)):
                            print("Moved closer → now using perception")
                            use_memory = False  # force perception after move

                    else:
                        print("Memory not reliable → ignoring")

            # --------------------------------------------------
            # STEP 3: MEMORY EXECUTION (ONLY IF SAFE)
            # --------------------------------------------------

            if use_memory:

                success = self._move_to(target_pos)

                if success:
                    print("Reached memory target, stabilizing...")

                    try:
                        self.movement.client.hoverAsync().join()
                    except:
                        pass

                    time.sleep(2)

                    target_found = True
                    break

            # --------------------------------------------------
            # STEP 4: OBJECT SEARCH (PRIMARY NOW)
            # --------------------------------------------------

            print("Using perception-based search...")

            target_pos = None

            print(f"[DEBUG] Searching for: {target}")

            try:
                target_pos = self.search_for_target_object.search(
                    target,
                    map_metadata,
                    self.landmark_memory
                )
            except Exception as e:
                print(f"Search error: {e}")

            print(f"[DEBUG] Search result: {target_pos}")

            if target_pos:

                print("Target found via search")

                target_found = True
                detection_success = True  # real detection success

                success = self._move_to(target_pos)

                if success:
                    print("Reached search target, stabilizing...")

                    try:
                        self.movement.client.hoverAsync().join()
                    except:
                        pass

                    time.sleep(2)

                    target_found = True

                # ONLY STORE IF REAL DETECTION HAPPENED
                # if target_found and detection_success:
                if target_found and detection_success and target_pos is not None:

                    try:
                        self.landmark_memory.add_landmark(
                            target,
                            list(target_pos)
                        )
                        print("[INFO] Stored VERIFIED landmark")
                    except:
                        pass
                else:
                    print("[INFO] Skipping memory storage (no real detection)")

                break

        # --------------------------------------------------
        # STEP 5: FALLBACK NAVIGATION
        # --------------------------------------------------

        if not target_found:

            print("Object not found → HOLDING POSITION (NO RANDOM NAVIGATION)")

            try:
                self.movement.client.hoverAsync().join()
            except:
                pass

            return

        # if not target_found:

        #     print("Object not found → using navigation fallback")

        #     try:
        #         self.vln_controller.execute_navigation(
        #             instruction,
        #             map_metadata,
        #             self.landmark_memory
        #         )
        #     except Exception as e:
        #         print(f"VLN navigation error: {e}")

    # --------------------------------------------------

    def _score_memory(self, entry, current_pos):

        try:
            pos = entry.get("pos")
            confidence = entry.get("confidence", 0.5)

            if not pos or len(pos) != 2:
                return 0

            dx = pos[0] - current_pos[0]
            dy = pos[1] - current_pos[1]

            distance = (dx**2 + dy**2) ** 0.5

            return confidence / (1 + distance)

        except:
            return 0

    # --------------------------------------------------

    def _move_to(self, target_pos):

        try:
            x, y = target_pos

            print(f"Moving to target: {target_pos}")

            # face target
            try:
                current_pos = self.movement.get_position()

                dx = x - current_pos[0]
                dy = y - current_pos[1]

                yaw = math.degrees(math.atan2(dy, dx))

                self.movement.client.rotateToYawAsync(yaw).join()

            except:
                pass

            success, _ = self.movement.move_to(
                x,
                y,
                self.altitude,
                self.speed
            )

            if not success:
                print("Movement failed")

            return success

        except Exception as e:
            print(f"Movement error: {e}")
            return False