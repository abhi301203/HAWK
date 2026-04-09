import json
import os


def load_config(config_path="config.json"):
    """
    Safely load configuration file
    """

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)


# --------------------------------------------------


def safe_shutdown(hawk):
    """
    Emergency-safe shutdown handler
    """

    try:
        if hawk and hasattr(hawk, "client"):

            print("\n[SAFETY] Performing emergency shutdown...")

            client = hawk.client

            try:
                client.hoverAsync().join()
            except:
                pass

            try:
                client.landAsync().join()
            except:
                pass

            try:
                client.armDisarm(False)
                client.enableApiControl(False)
            except:
                pass

            print("[SAFETY] Shutdown complete")

    except Exception as e:
        print(f"[SAFETY] Shutdown failed: {e}")


# --------------------------------------------------


def main():

    print("\n========== HAWK SYSTEM START ==========\n")

    hawk = None
    results = None  # ✅ FIXED

    # ---------- LOAD CONFIG ----------

    try:
        config = load_config()
        print("[INFO] Config loaded successfully")
    except Exception as e:
        print(f"[ERROR] Failed to load config: {e}")
        return

    # ---------- INITIALIZE CONTROLLER ----------

    try:
        from hawk_system.hawk_controller import HawkController

        hawk = HawkController(config)

        print("[INFO] HawkController initialized")

    except Exception as e:
        print(f"[ERROR] Initialization failed: {e}")
        return

    # ---------- RUN SYSTEM ----------

    try:

        print("\n[INFO] Starting execution...\n")

        results = hawk.run()

    except KeyboardInterrupt:
        print("\n[WARNING] Execution interrupted by user")

    except Exception as e:
        print(f"[ERROR] Runtime error: {e}")

    finally:
        # ---------- ALWAYS SAFE SHUTDOWN ----------

        safe_shutdown(hawk)

    # ---------- FINAL OUTPUT ----------

    if results is not None:

        # Only print for exploration mode
        if isinstance(results, dict) and results.get("images_captured", 0) > 0:
            print("\n========== EXPLORATION RESULTS ==========")
            print(results)

    print("\n========== HAWK SYSTEM END ==========\n")


# --------------------------------------------------

if __name__ == "__main__":
    main()