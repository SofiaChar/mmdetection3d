import os
import time
import json
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# Function to find the latest temp directory that starts with "2024"
def get_latest_temp_dir(base_path="/valohai/outputs", prefix="2024"):
    try:
        # List all directories in the base path that start with the given prefix (e.g., "2024")
        temp_dirs = [d for d in os.listdir(base_path) if d.startswith(prefix) and os.path.isdir(os.path.join(base_path, d))]

        if not temp_dirs:
            return None

        # Sort the directories by modification time (most recent first)
        temp_dirs.sort(key=lambda d: os.path.getmtime(os.path.join(base_path, d)), reverse=True)

        # Return the full path to the latest directory
        latest_dir = os.path.join(base_path, temp_dirs[0])
        return latest_dir
    except Exception as e:
        print(f"WATCHDOG - Error finding the latest temp directory: {e}")
        return None

# Polling function to wait until the temp folder and scalars.json file are created
def wait_for_temp_dir_and_file(base_path="/valohai/outputs", prefix="2024", timeout=300, poll_interval=5):
    start_time = time.time()
    latest_dir = None

    while (time.time() - start_time) < timeout:
        latest_dir = get_latest_temp_dir(base_path, prefix)
        if latest_dir:
            print(f"WATCHDOG - Temp directory found: {latest_dir}")

            # Check for the scalars.json file inside the vis_data folder
            scalars_file_path = os.path.join(latest_dir, "vis_data/scalars.json")
            if os.path.exists(scalars_file_path):
                print(f"WATCHDOG - scalars.json file found: {scalars_file_path}")
                return scalars_file_path  # Return the file path once found
            else:
                print(f"WATCHDOG - Waiting for scalars.json to be created in {latest_dir}...")
        else:
            print(f"WATCHDOG - Waiting for temp directory starting with '{prefix}' to be created...")

        time.sleep(poll_interval)

    raise TimeoutError(f"WATCHDOG - Temp directory or scalars.json file not found within {timeout} seconds.")

# Watchdog handler class for monitoring updates to scalars.json
class ValohaiHandler(PatternMatchingEventHandler):
    def __init__(self, patterns=None):
        super().__init__(patterns=patterns)
        self.total_iters_per_epoch = 3712

    def on_modified(self, event):
        print('WATCHDOG - event.src_path is: ', event.src_path)
        if "scalars.json" in event.src_path:
            try:
                # Read the scalars.json file line by line (each line is a JSON object)
                with open(event.src_path, "r") as file:
                    lines = file.readlines()

                # Process the last JSON object (last line)
                if lines:
                    last_line = lines[-1].strip()  # Get the last line and strip any extra whitespace
                    # print(f"WATCHDOG - Last JSON line: {last_line}")

                    # Parse the last JSON line
                    last_entry = json.loads(last_line)

                    # Compute the continuous iteration metric
                    epoch = last_entry.get('epoch', 0)
                    iter_ = last_entry.get('iter', 0)
                    continuous_iter = (epoch - 1) * self.total_iters_per_epoch + iter_

                    # Add continuous iteration to the entry
                    last_entry['continuous_iter'] = continuous_iter
                    print(json.dumps(last_entry))  # Pretty-print the last JSON object

            except json.JSONDecodeError as e:
                print(f"WATCHDOG - Error reading or parsing the file: {e}")
            except Exception as e:
                print(f"WATCHDOG - General error reading the file: {e}")

# Main logic
if __name__ == "__main__":
    try:
        # Wait for the temp directory and scalars.json file in /valohai/outputs that starts with "2024"
        scalars_file_path = wait_for_temp_dir_and_file()

        # Set up the event handler to monitor for changes to scalars.json
        event_handler = ValohaiHandler(patterns=["*.json"])
        observer = Observer()

        # Start the observer, recursively watching the vis_data directory
        observer.schedule(event_handler, path=os.path.dirname(scalars_file_path), recursive=False)
        observer.start()

        print(f"WATCHDOG - Started watching {scalars_file_path} for changes...")

        try:
            # Keep the script running to monitor file changes
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    except TimeoutError as e:
        print(e)
